"""
YouTube Data API client for fetching channel and video data
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import get_settings

settings = get_settings()


class YouTubeClient:
    """YouTube Data API v3 client"""
    
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
    
    def extract_channel_id(self, url: str) -> Optional[str]:
        """
        Extract channel ID from various YouTube URL formats
        
        Supported formats:
        - https://youtube.com/@username
        - https://youtube.com/channel/UC123...
        - https://youtube.com/c/channelname
        - https://youtube.com/user/username
        
        Args:
            url: YouTube channel URL
            
        Returns:
            Channel ID or None if invalid
        """
        # Direct channel ID format
        channel_id_match = re.search(r'youtube\.com/channel/([a-zA-Z0-9_-]+)', url)
        if channel_id_match:
            return channel_id_match.group(1)
        
        # Handle @username format
        handle_match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)', url)
        if handle_match:
            handle = handle_match.group(1)
            return self._resolve_handle_to_channel_id(handle)
        
        # Handle /c/ format
        custom_match = re.search(r'youtube\.com/c/([a-zA-Z0-9_-]+)', url)
        if custom_match:
            custom_name = custom_match.group(1)
            return self._resolve_custom_url_to_channel_id(custom_name)
        
        # Handle /user/ format
        user_match = re.search(r'youtube\.com/user/([a-zA-Z0-9_-]+)', url)
        if user_match:
            username = user_match.group(1)
            return self._resolve_username_to_channel_id(username)
        
        return None
    
    def _resolve_handle_to_channel_id(self, handle: str) -> Optional[str]:
        """Resolve @handle to channel ID using search API"""
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=f'@{handle}',
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
            return None
        except HttpError:
            return None
    
    def _resolve_custom_url_to_channel_id(self, custom_name: str) -> Optional[str]:
        """Resolve custom URL to channel ID"""
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=custom_name,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
            return None
        except HttpError:
            return None
    
    def _resolve_username_to_channel_id(self, username: str) -> Optional[str]:
        """Resolve username to channel ID"""
        try:
            request = self.youtube.channels().list(
                part='id',
                forUsername=username
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['id']
            return None
        except HttpError:
            return None
    
    def get_channel_metadata(self, channel_id: str) -> Optional[Dict]:
        """
        Fetch channel metadata from YouTube Data API
        
        API Cost: 1 quota unit
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel metadata dict or None if not found
        """
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']
            content_details = channel['contentDetails']
            
            return {
                'channel_id': channel_id,
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'custom_url': snippet.get('customUrl'),
                'published_at': snippet.get('publishedAt'),
                'country': snippet.get('country'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'upload_playlist_id': content_details['relatedPlaylists']['uploads']
            }
        except HttpError as e:
            print(f"YouTube API error fetching channel {channel_id}: {e}")
            return None
    
    def get_channel_videos(self, upload_playlist_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch video list from channel's upload playlist
        
        API Cost: 1 quota unit per 50 videos (pagination)
        
        Args:
            upload_playlist_id: Channel's upload playlist ID
            max_results: Maximum number of videos to fetch
            
        Returns:
            List of video metadata dicts
        """
        videos = []
        next_page_token = None
        
        try:
            while len(videos) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=upload_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item['snippet']
                    videos.append({
                        'video_id': item['contentDetails']['videoId'],
                        'title': snippet.get('title'),
                        'description': snippet.get('description'),
                        'published_at': snippet.get('publishedAt'),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url')
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos[:max_results]
        
        except HttpError as e:
            print(f"YouTube API error fetching videos from playlist {upload_playlist_id}: {e}")
            return videos
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Fetch detailed video metadata
        
        API Cost: 1 quota unit per request (max 50 videos per request)
        
        Args:
            video_ids: List of video IDs (max 50)
            
        Returns:
            List of detailed video metadata
        """
        if not video_ids:
            return []
        
        # YouTube API allows max 50 IDs per request
        video_ids = video_ids[:50]
        
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                snippet = item['snippet']
                content_details = item['contentDetails']
                statistics = item.get('statistics', {})
                
                videos.append({
                    'video_id': item['id'],
                    'channel_id': snippet['channelId'],
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'published_at': snippet.get('publishedAt'),
                    'duration': content_details.get('duration'),
                    'tags': snippet.get('tags', []),
                    'category_id': snippet.get('categoryId'),
                    'view_count': int(statistics.get('viewCount', 0)),
                    'like_count': int(statistics.get('likeCount', 0)),
                    'comment_count': int(statistics.get('commentCount', 0))
                })
            
            return videos
        
        except HttpError as e:
            print(f"YouTube API error fetching video details: {e}")
            return []
    
    def select_representative_videos(
        self, 
        all_videos: List[Dict], 
        max_videos: int = 50
    ) -> Tuple[List[str], str]:
        """
        Select representative video sample using intelligent strategy
        
        Strategy:
        - < 50 videos: Use all
        - 50-500 videos: Recent 30 + top 10 by views + 10 distributed
        - 500+ videos: Recent 20 + top 15 + 15 distributed
        
        Args:
            all_videos: List of all video metadata
            max_videos: Maximum videos to select
            
        Returns:
            Tuple of (selected_video_ids, strategy_used)
        """
        total = len(all_videos)
        
        if total <= max_videos:
            return [v['video_id'] for v in all_videos], "all_videos"
        
        # Need to fetch detailed stats for intelligent selection
        # For now, use a simpler strategy based on published_at
        
        if total <= 500:
            # Take most recent 30 and evenly distributed 20
            recent = all_videos[:30]
            step = max(1, (total - 30) // 20)
            distributed = all_videos[30::step][:20]
            selected = recent + distributed
            return [v['video_id'] for v in selected[:max_videos]], "recent_distributed"
        else:
            # Large channel: recent 25 and distributed 25
            recent = all_videos[:25]
            step = max(1, total // 25)
            distributed = all_videos[25::step][:25]
            selected = recent + distributed
            return [v['video_id'] for v in selected[:max_videos]], "large_channel_sample"


# Global YouTube client instance
youtube_client = YouTubeClient()
