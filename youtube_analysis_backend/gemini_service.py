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
    
    def prepare_analysis_prompt(
        self, 
        channel_metadata: Dict, 
        videos: List[Dict]
    ) -> str:
        """
        Prepare structured prompt for Gemini analysis
        
        Args:
            channel_metadata: Channel metadata from YouTube
            videos: List of video metadata
            
        Returns:
            Formatted prompt string
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
        
        # Analysis instructions
        task = """Based on the channel and video data above, provide a comprehensive analysis in the following JSON format:

{
  "summary": "A concise 3-paragraph summary describing what this channel is about, its main focus, and value proposition",
  "themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
  "target_audience": "Detailed description of the primary target audience",
  "content_style": "Description of the content style, tone, and presentation approach",
  "upload_frequency": "Estimated upload frequency pattern (e.g., 'daily', '2-3 times per week', 'weekly', 'irregular')",
  "confidence_score": 0.95
}

Important guidelines:
1. Base your analysis ONLY on the provided data - do not hallucinate
2. The summary should be factual and insightful
3. Themes should be specific topics or categories covered
4. Confidence score should reflect data quality (0.0-1.0)
5. Return ONLY valid JSON, no additional text

"""
        
        return channel_info + video_info + task
    
    def analyze_channel(
        self, 
        channel_metadata: Dict, 
        videos: List[Dict],
        use_caching: bool = True
    ) -> Optional[Dict]:
        """
        Analyze channel using Gemini AI
        
        Args:
            channel_metadata: Channel metadata
            videos: List of video metadata
            use_caching: Whether to use context caching
            
        Returns:
            Analysis results dict or None on error
        """
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
