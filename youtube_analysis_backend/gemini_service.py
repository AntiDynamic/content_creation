"""
Gemini AI service for channel analysis
"""
from typing import Dict, List, Optional
import json
from google import genai
from google.genai import types
from config import get_settings

settings = get_settings()


class GeminiAnalyzer:
    """Gemini AI analyzer for YouTube channels"""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
    
    def prepare_strategic_analysis_prompt(
        self, 
        channel_metadata: Dict, 
        top_videos: List[Dict],
        recent_videos: List[Dict]
    ) -> str:
        """
        Prepare strategic analysis prompt for deep channel guidance
        
        Args:
            channel_metadata: Channel metadata from YouTube
            top_videos: Top performing videos by views
            recent_videos: Most recent videos
            
        Returns:
            Formatted prompt string
        """
        # Format channel info
        channel_info = f"""=== CHANNEL PROFILE ===
Channel Name: {channel_metadata.get('title')}
Description: {channel_metadata.get('description', 'N/A')[:500]}
Subscribers: {channel_metadata.get('subscriber_count', 0):,}
Total Videos: {channel_metadata.get('video_count', 0):,}
Total Views: {channel_metadata.get('view_count', 0):,}
Active Since: {channel_metadata.get('published_at', 'Unknown')}
Country: {channel_metadata.get('country', 'Unknown')}

Average Views per Video: {channel_metadata.get('view_count', 0) // max(channel_metadata.get('video_count', 1), 1):,}

"""
        
        # Format top performing videos
        top_video_info = "=== TOP PERFORMING VIDEOS (By Views) ===\n\n"
        for idx, video in enumerate(top_videos, 1):
            engagement_rate = (video.get('like_count', 0) / max(video.get('view_count', 1), 1)) * 100
            top_video_info += f"""#{idx} - {video.get('title')}
   Views: {video.get('view_count', 0):,} | Likes: {video.get('like_count', 0):,} | Comments: {video.get('comment_count', 0):,}
   Engagement Rate: {engagement_rate:.2f}%
   Published: {video.get('published_at')}
   Duration: {video.get('duration', 'Unknown')}
   Tags: {', '.join(video.get('tags', [])[:5]) or 'None'}

"""
        
        # Format recent videos
        recent_video_info = "=== MOST RECENT VIDEOS ===\n\n"
        for idx, video in enumerate(recent_videos, 1):
            engagement_rate = (video.get('like_count', 0) / max(video.get('view_count', 1), 1)) * 100
            recent_video_info += f"""#{idx} - {video.get('title')}
   Views: {video.get('view_count', 0):,} | Likes: {video.get('like_count', 0):,} | Comments: {video.get('comment_count', 0):,}
   Engagement Rate: {engagement_rate:.2f}%
   Published: {video.get('published_at')}
   Duration: {video.get('duration', 'Unknown')}
   Tags: {', '.join(video.get('tags', [])[:5]) or 'None'}

"""
        
        # Strategic analysis instructions
        task = """=== YOUR TASK ===
You are an expert YouTube Growth Strategist. Analyze this channel and provide ACTIONABLE guidance.

Return ONLY this JSON (no markdown, no code blocks):

{
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "growth_strategy": [
    {"priority": "HIGH", "action": "What to do", "expected_impact": "Expected result", "timeline": "How long"},
    {"priority": "MEDIUM", "action": "What to do", "expected_impact": "Expected result", "timeline": "How long"},
    {"priority": "LOW", "action": "What to do", "expected_impact": "Expected result", "timeline": "How long"}
  ],
  "content_recommendations": [
    {"type": "Content type", "description": "Why this works", "frequency": "How often", "example_topics": ["topic1", "topic2", "topic3"]}
  ],
  "thumbnail_advice": "Specific thumbnail tips based on top videos",
  "title_advice": "Specific title optimization tips",
  "upload_schedule": "Recommended upload schedule",
  "engagement_tips": ["tip 1", "tip 2", "tip 3"],
  "scores": {"overall": 75, "consistency": 70, "engagement": 80, "growth_potential": 85},
  "overall_verdict": "2-3 sentence summary of the channel and most important advice"
}

Be SPECIFIC and reference actual data. Scores 0-100.
"""
        
        return channel_info + top_video_info + recent_video_info + task
    
    def prepare_analysis_prompt(
        self, 
        channel_metadata: Dict, 
        videos: List[Dict]
    ) -> str:
        """
        Prepare structured prompt for Gemini analysis (legacy)
        """
        # Format channel info
        channel_info = f"""Channel Information:
- Title: {channel_metadata.get('title')}
- Description: {channel_metadata.get('description', 'N/A')[:500]}
- Subscriber Count: {channel_metadata.get('subscriber_count', 0):,}
- Total Videos: {channel_metadata.get('video_count', 0):,}
- Active Since: {channel_metadata.get('published_at', 'Unknown')}
- Country: {channel_metadata.get('country', 'Unknown')}

"""
        
        # Format video sample
        video_info = f"Video Sample Analysis ({len(videos)} representative videos):\n\n"
        
        for idx, video in enumerate(videos, 1):
            video_info += f"""Video {idx}:
- Title: {video.get('title')}
- Description: {video.get('description', 'N/A')[:200]}
- Views: {video.get('view_count', 0):,}
- Likes: {video.get('like_count', 0):,}
- Published: {video.get('published_at')}
- Duration: {video.get('duration', 'Unknown')}
- Tags: {', '.join(video.get('tags', [])[:5])}

"""
        
        task = """Based on the channel and video data above, provide a comprehensive analysis in the following JSON format:

{
  "summary": "A concise 3-paragraph summary describing what this channel is about, its main focus, and value proposition",
  "themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
  "target_audience": "Detailed description of the primary target audience",
  "content_style": "Description of the content style, tone, and presentation approach",
  "upload_frequency": "Estimated upload frequency pattern",
  "confidence_score": 0.95
}

Return ONLY valid JSON, no additional text.
"""
        
        return channel_info + video_info + task
    
    def analyze_channel_strategic(
        self, 
        channel_metadata: Dict, 
        top_videos: List[Dict],
        recent_videos: List[Dict]
    ) -> Optional[Dict]:
        """
        Perform deep strategic analysis of channel
        """
        try:
            prompt = self.prepare_strategic_analysis_prompt(channel_metadata, top_videos, recent_videos)
            
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8000,
                system_instruction=(
                    "You are an expert YouTube Growth Strategist with 10+ years of experience helping creators grow. "
                    "You analyze channels deeply and provide specific, actionable advice based on data. "
                    "Always respond with valid JSON only - no markdown code blocks, no extra text."
                )
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            response_text = response.text.strip()
            print(f"DEBUG: Strategic analysis response length: {len(response_text)}")
            print(f"DEBUG: Response preview: {response_text[:500]}...")
            
            # Extract JSON - improved extraction
            json_text = response_text
            
            # Handle markdown code blocks
            if '```json' in response_text:
                # Find the start after ```json
                json_start = response_text.find('```json') + 7
                # Find the closing ```
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
                    print(f"DEBUG: Extracted from ```json block, length: {len(json_text)}")
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                # Skip any language identifier on the same line
                newline_pos = response_text.find('\n', json_start)
                if newline_pos > json_start:
                    json_start = newline_pos + 1
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
                    print(f"DEBUG: Extracted from ``` block, length: {len(json_text)}")
            
            # If still doesn't start with {, try to find JSON object
            if not json_text.startswith('{'):
                brace_start = json_text.find('{')
                brace_end = json_text.rfind('}') + 1
                if brace_start >= 0 and brace_end > brace_start:
                    json_text = json_text[brace_start:brace_end]
                    print(f"DEBUG: Extracted raw JSON from braces, length: {len(json_text)}")
            
            print(f"DEBUG: Final JSON text preview: {json_text[:300]}...")
            
            analysis = json.loads(json_text)
            analysis['model_version'] = self.model
            analysis['top_videos_analyzed'] = len(top_videos)
            analysis['recent_videos_analyzed'] = len(recent_videos)
            
            print(f"DEBUG: Strategic analysis successful!")
            return analysis
            
        except Exception as e:
            print(f"Strategic analysis error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_channel(
        self, 
        channel_metadata: Dict, 
        videos: List[Dict],
        use_caching: bool = True
    ) -> Optional[Dict]:
        try:
            prompt = self.prepare_analysis_prompt(channel_metadata, videos)
            
            # Configure generation
            config = types.GenerateContentConfig(
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_output_tokens,
                system_instruction=(
                    "You are a YouTube analytics expert. Analyze channel data and provide "
                    "factual, concise insights in valid JSON format. Do not hallucinate or "
                    "make assumptions beyond the provided data."
                )
            )
            
            # Generate analysis
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Parse response
            response_text = response.text.strip()
            print(f"DEBUG: Raw Gemini response length: {len(response_text)}")
            
            # Extract JSON from response (handle multiple formats)
            json_text = response_text
            
            # Try to find JSON in markdown code blocks first
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
            else:
                # Try to find JSON object boundaries
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
            
            print(f"DEBUG: Extracted JSON length: {len(json_text)}")
            print(f"DEBUG: First 200 chars: {json_text[:200]}")
            
            # Parse JSON
            try:
                analysis = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse Gemini response as JSON: {e}")
                print(f"Full response text:\n{response_text}")
                return None
            
            # Validate required fields
            required_fields = ['summary', 'themes', 'target_audience', 'content_style', 'upload_frequency']
            if not all(field in analysis for field in required_fields):
                print(f"Missing required fields in Gemini response: {analysis.keys()}")
                return None
            
            # Add metadata
            analysis['model_version'] = self.model
            analysis['analyzed_videos_count'] = len(videos)
            analysis['total_videos_count'] = channel_metadata.get('video_count', 0)
            
            # Ensure confidence score
            if 'confidence_score' not in analysis:
                analysis['confidence_score'] = 0.85  # Default
            
            print(f"DEBUG: Analysis successful! Keys: {list(analysis.keys())}")
            return analysis
        
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_channel_streaming(
        self, 
        channel_metadata: Dict, 
        videos: List[Dict]
    ):
        """
        Analyze channel with streaming response (for real-time UI updates)
        
        Args:
            channel_metadata: Channel metadata
            videos: List of video metadata
            
        Yields:
            Response chunks
        """
        try:
            prompt = self.prepare_analysis_prompt(channel_metadata, videos)
            
            config = types.GenerateContentConfig(
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_output_tokens,
                system_instruction=(
                    "You are a YouTube analytics expert. Analyze channel data and provide "
                    "factual, concise insights in valid JSON format."
                )
            )
            
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            for chunk in response:
                yield chunk.text
        
        except Exception as e:
            print(f"Gemini streaming error: {e}")
            yield json.dumps({"error": str(e)})


# Global Gemini analyzer instance
gemini_analyzer = GeminiAnalyzer()
