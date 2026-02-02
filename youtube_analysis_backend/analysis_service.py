"""
Main analysis orchestration service
Implements the complete workflow from channel URL to analysis results
"""
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import hashlib
from sqlalchemy.orm import Session

from models import Channel, Video, ChannelAnalysis
from cache import cache
from youtube_service import youtube_client
from gemini_service import gemini_analyzer
from config import get_settings

settings = get_settings()


class AnalysisService:
    """Orchestrates the complete channel analysis workflow"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_channel(self, channel_url: str) -> Dict:
        """
        Main workflow: Analyze a YouTube channel
        
        Steps:
        1. Extract and validate channel ID
        2. Check for existing analysis (cache → database)
        3. Fetch channel metadata
        4. Fetch and sample videos
        5. Get detailed video data
        6. Analyze with Gemini
        7. Store results
        8. Return response
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            Analysis result dict with metadata
        """
        # Step 1: Extract channel ID
        channel_id = self._get_channel_id_from_url(channel_url)
        if not channel_id:
            return {
                'success': False,
                'error': 'Invalid YouTube channel URL',
                'error_code': 'INVALID_URL'
            }
        
        # Step 2: Check for existing analysis
        existing_analysis = self._get_existing_analysis(channel_id)
        if existing_analysis:
            return {
                'success': True,
                'data': existing_analysis,
                'source': 'cache' if existing_analysis.get('_from_cache') else 'database'
            }
        
        # Step 3: Fetch channel metadata
        channel_metadata = self._fetch_and_store_channel_metadata(channel_id)
        if not channel_metadata:
            return {
                'success': False,
                'error': 'Channel not found or API error',
                'error_code': 'CHANNEL_NOT_FOUND'
            }
        
        # Step 4: Fetch video list
        videos_list = self._fetch_video_list(channel_metadata['upload_playlist_id'])
        if not videos_list:
            return {
                'success': False,
                'error': 'No videos found on channel',
                'error_code': 'NO_VIDEOS'
            }
        
        # Step 5: Select representative sample and get details
        video_ids, sampling_strategy = youtube_client.select_representative_videos(
            videos_list, 
            settings.max_videos_to_analyze
        )
        
        detailed_videos = youtube_client.get_video_details(video_ids)
        if not detailed_videos:
            return {
                'success': False,
                'error': 'Failed to fetch video details',
                'error_code': 'VIDEO_FETCH_ERROR'
            }
        
        # Store video metadata
        self._store_video_metadata(detailed_videos)
        
        # Step 6: Analyze with Gemini
        print(f"DEBUG: Starting Gemini analysis with {len(detailed_videos)} videos...")
        try:
            analysis_result = gemini_analyzer.analyze_channel(
                channel_metadata, 
                detailed_videos,
                use_caching=settings.enable_context_caching
            )
            print(f"DEBUG: Gemini analysis result: {analysis_result is not None}")
        except Exception as e:
            print(f"DEBUG: Gemini analysis exception: {e}")
            import traceback
            traceback.print_exc()
            analysis_result = None
        
        if not analysis_result:
            print("DEBUG: Analysis failed - returning error")
            return {
                'success': False,
                'error': 'AI analysis failed',
                'error_code': 'ANALYSIS_FAILED'
            }
        
        # Step 7: Store analysis results
        stored_analysis = self._store_analysis(
            channel_id=channel_id,
            analysis_result=analysis_result,
            video_sample_ids=video_ids
        )
        
        # Step 8: Format and return response
        response_data = self._format_analysis_response(
            channel_metadata=channel_metadata,
            analysis=stored_analysis
        )
        
        return {
            'success': True,
            'data': response_data,
            'source': 'fresh_analysis'
        }
    
    def _get_channel_id_from_url(self, url: str) -> Optional[str]:
        """Extract channel ID from URL with caching"""
        # Create hash of URL for cache key
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Check cache
        cached_id = cache.get_url_mapping(url_hash)
        if cached_id:
            return cached_id
        
        # Extract channel ID
        channel_id = youtube_client.extract_channel_id(url)
        
        # Cache the mapping
        if channel_id:
            cache.set_url_mapping(url_hash, channel_id)
        
        return channel_id
    
    def _get_existing_analysis(self, channel_id: str) -> Optional[Dict]:
        """
        Check for existing analysis in cache and database
        
        Priority:
        1. Cache (fastest)
        2. Database (if not expired)
        3. None (trigger fresh analysis)
        """
        # Check cache first
        cached_analysis = cache.get_channel_analysis(channel_id)
        if cached_analysis:
            cached_analysis['_from_cache'] = True
            return cached_analysis
        
        # Check database
        db_analysis = self.db.query(ChannelAnalysis).filter(
            ChannelAnalysis.channel_id == channel_id
        ).first()
        
        if db_analysis and not db_analysis.is_expired:
            # Load from database and cache it
            analysis_dict = {
                'channel_id': db_analysis.channel_id,
                'summary': db_analysis.summary,
                'themes': db_analysis.themes,
                'target_audience': db_analysis.target_audience,
                'content_style': db_analysis.content_style,
                'upload_frequency': db_analysis.upload_frequency,
                'analyzed_videos_count': db_analysis.analyzed_videos_count,
                'total_videos_count': db_analysis.total_videos_count,
                'confidence_score': db_analysis.confidence_score,
                'analyzed_at': db_analysis.analyzed_at.isoformat(),
                'freshness': db_analysis.freshness,
                '_from_cache': False
            }
            
            # Cache for future requests
            cache.set_channel_analysis(channel_id, analysis_dict)
            
            return analysis_dict
        
        return None
    
    def _fetch_and_store_channel_metadata(self, channel_id: str) -> Optional[Dict]:
        """Fetch channel metadata and store in database + cache"""
        # Check cache first
        cached_metadata = cache.get_channel_metadata(channel_id)
        if cached_metadata:
            return cached_metadata
        
        # Fetch from YouTube
        metadata = youtube_client.get_channel_metadata(channel_id)
        if not metadata:
            return None
        
        # Store in database
        channel = self.db.query(Channel).filter(Channel.channel_id == channel_id).first()
        
        if channel:
            # Update existing
            channel.title = metadata['title']
            channel.description = metadata['description']
            channel.subscriber_count = metadata['subscriber_count']
            channel.video_count = metadata['video_count']
            channel.view_count = metadata['view_count']
            channel.updated_at = datetime.utcnow()
        else:
            # Create new
            channel = Channel(
                channel_id=metadata['channel_id'],
                title=metadata['title'],
                description=metadata['description'],
                subscriber_count=metadata['subscriber_count'],
                video_count=metadata['video_count'],
                view_count=metadata['view_count'],
                upload_playlist_id=metadata['upload_playlist_id'],
                published_at=datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00')) if metadata.get('published_at') else None,
                country=metadata.get('country'),
                custom_url=metadata.get('custom_url'),
                thumbnail_url=metadata.get('thumbnail_url')
            )
            self.db.add(channel)
        
        self.db.commit()
        
        # Cache metadata
        cache.set_channel_metadata(channel_id, metadata)
        
        return metadata
    
    def _fetch_video_list(self, upload_playlist_id: str) -> list:
        """Fetch video list from channel"""
        return youtube_client.get_channel_videos(
            upload_playlist_id, 
            max_results=500  # Fetch more for better sampling
        )
    
    def _store_video_metadata(self, videos: list):
        """Store video metadata in database"""
        for video_data in videos:
            video = self.db.query(Video).filter(Video.video_id == video_data['video_id']).first()
            
            if not video:
                video = Video(
                    video_id=video_data['video_id'],
                    channel_id=video_data['channel_id'],
                    title=video_data['title'],
                    description=video_data['description'],
                    published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')) if video_data.get('published_at') else None,
                    duration=video_data.get('duration'),
                    view_count=video_data.get('view_count'),
                    like_count=video_data.get('like_count'),
                    comment_count=video_data.get('comment_count'),
                    tags=video_data.get('tags', []),
                    category_id=video_data.get('category_id')
                )
                self.db.add(video)
        
        self.db.commit()
    
    def _store_analysis(
        self, 
        channel_id: str, 
        analysis_result: Dict,
        video_sample_ids: list
    ) -> ChannelAnalysis:
        """Store analysis results in database"""
        # Check if analysis already exists
        existing = self.db.query(ChannelAnalysis).filter(
            ChannelAnalysis.channel_id == channel_id
        ).first()
        
        analyzed_at = datetime.utcnow()
        expires_at = analyzed_at + timedelta(days=settings.analysis_expiry_days)
        
        if existing:
            # Update existing
            existing.summary = analysis_result['summary']
            existing.themes = analysis_result['themes']
            existing.target_audience = analysis_result['target_audience']
            existing.content_style = analysis_result['content_style']
            existing.upload_frequency = analysis_result['upload_frequency']
            existing.analyzed_videos_count = analysis_result['analyzed_videos_count']
            existing.total_videos_count = analysis_result['total_videos_count']
            existing.confidence_score = analysis_result.get('confidence_score', 0.85)
            existing.model_version = analysis_result['model_version']
            existing.analyzed_at = analyzed_at
            existing.expires_at = expires_at
            existing.video_sample_ids = video_sample_ids
            analysis = existing
        else:
            # Create new
            analysis = ChannelAnalysis(
                channel_id=channel_id,
                summary=analysis_result['summary'],
                themes=analysis_result['themes'],
                target_audience=analysis_result['target_audience'],
                content_style=analysis_result['content_style'],
                upload_frequency=analysis_result['upload_frequency'],
                analyzed_videos_count=analysis_result['analyzed_videos_count'],
                total_videos_count=analysis_result['total_videos_count'],
                confidence_score=analysis_result.get('confidence_score', 0.85),
                model_version=analysis_result['model_version'],
                analyzed_at=analyzed_at,
                expires_at=expires_at,
                video_sample_ids=video_sample_ids
            )
            self.db.add(analysis)
        
        self.db.commit()
        self.db.refresh(analysis)
        
        return analysis
    
    def _format_analysis_response(
        self, 
        channel_metadata: Dict, 
        analysis: ChannelAnalysis
    ) -> Dict:
        """Format final response for API"""
        return {
            'channel': {
                'id': channel_metadata['channel_id'],
                'title': channel_metadata['title'],
                'subscriber_count': channel_metadata['subscriber_count'],
                'video_count': channel_metadata['video_count'],
                'thumbnail_url': channel_metadata.get('thumbnail_url')
            },
            'analysis': {
                'summary': analysis.summary,
                'themes': analysis.themes,
                'target_audience': analysis.target_audience,
                'content_style': analysis.content_style,
                'upload_frequency': analysis.upload_frequency
            },
            'meta': {
                'analyzed_at': analysis.analyzed_at.isoformat(),
                'videos_analyzed': analysis.analyzed_videos_count,
                'total_videos': analysis.total_videos_count,
                'freshness': analysis.freshness,
                'confidence': analysis.confidence_score,
                'model_version': analysis.model_version
            }
        }
