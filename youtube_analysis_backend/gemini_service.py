"""
Gemini AI service for channel analysis
"""
from typing import Dict, List, Optional
import json
from google import genai
from google.genai import types
from config import get_settings

settings = get_settings()

# YouTube Growth Strategist System Prompt
GROWTH_STRATEGIST_SYSTEM_PROMPT = """You are a YouTube growth strategist and creator coach.

Your primary goal is NOT to sound impressive.
Your goal is to increase the probability of views for THIS specific creator.

You must behave like a real human mentor:
- practical
- realistic
- personalized
- step-by-step
- honest about constraints

CORE PRINCIPLE (NON-NEGOTIABLE):
Only suggest ideas that satisfy ALL of the following:
1. There is current audience demand
2. The format aligns with what YouTube is currently pushing
3. It fits THIS channel's size and history
4. It matches the creator's effort level
5. It reduces friction for the viewer (clear hook, simple payoff)

If any condition fails, DO NOT suggest it.

LANGUAGE & TONE RULES:
- Be clear, calm, and practical
- Explain "why" behind every suggestion
- Speak directly to the creator
- Avoid buzzwords and hype

ABSOLUTE RESTRICTIONS:
- Do NOT give generic YouTube advice
- Do NOT give everything at once
- Do NOT suggest anything the creator cannot realistically execute
- Do NOT act like an algorithm "hacker"
- Never promise virality or guaranteed views

You are optimizing for learning + probability of growth, not shortcuts."""


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

    def prepare_phase_prompt(
        self,
        phase: int,
        channel_metadata: Dict,
        top_videos: List[Dict],
        recent_videos: List[Dict],
        creator_profile: Optional[Dict] = None,
        previous_phases: Optional[Dict] = None,
        user_message: Optional[str] = None
    ) -> str:
        """
        Prepare prompt for each coaching phase
        
        Args:
            phase: Current phase number (1-6)
            channel_metadata: Channel metadata from YouTube
            top_videos: Top performing videos by views
            recent_videos: Most recent videos
            creator_profile: Creator's preferences and goals
            previous_phases: Results from previous phases
            user_message: Optional user input/response
        """
        # Format channel data
        channel_info = f"""=== CHANNEL DATA ===
Channel Name: {channel_metadata.get('title')}
Description: {channel_metadata.get('description', 'N/A')[:500]}
Subscribers: {channel_metadata.get('subscriber_count', 0):,}
Total Videos: {channel_metadata.get('video_count', 0):,}
Total Views: {channel_metadata.get('view_count', 0):,}
Active Since: {channel_metadata.get('published_at', 'Unknown')}

"""
        
        # Format top videos
        top_video_info = "=== TOP PERFORMING VIDEOS ===\n"
        for idx, video in enumerate(top_videos[:5], 1):
            engagement_rate = (video.get('like_count', 0) / max(video.get('view_count', 1), 1)) * 100
            top_video_info += f"""#{idx}: {video.get('title')}
   Views: {video.get('view_count', 0):,} | Engagement: {engagement_rate:.2f}%
   Duration: {video.get('duration', 'Unknown')} | Published: {video.get('published_at')}
"""
        
        # Format recent videos
        recent_video_info = "\n=== MOST RECENT VIDEOS ===\n"
        for idx, video in enumerate(recent_videos[:5], 1):
            engagement_rate = (video.get('like_count', 0) / max(video.get('view_count', 1), 1)) * 100
            recent_video_info += f"""#{idx}: {video.get('title')}
   Views: {video.get('view_count', 0):,} | Engagement: {engagement_rate:.2f}%
   Duration: {video.get('duration', 'Unknown')} | Published: {video.get('published_at')}
"""
        
        # Format creator profile if available
        creator_info = ""
        if creator_profile:
            creator_info = f"""
=== CREATOR PREFERENCES ===
Preferred Genres: {', '.join(creator_profile.get('preferred_genres', [])) or 'Not specified'}
Future Goals: {creator_profile.get('future_goals', 'Not specified')}
Time Horizon: {creator_profile.get('time_horizon', 'Not specified')}
Effort Level: {creator_profile.get('effort_level', 'Not specified')}
Content Frequency: {creator_profile.get('content_frequency', 'Not specified')}
Equipment Level: {creator_profile.get('equipment_level', 'Not specified')}
Editing Skills: {creator_profile.get('editing_skills', 'Not specified')}
Current Challenges: {', '.join(creator_profile.get('current_challenges', [])) or 'Not specified'}
Topics to Avoid: {', '.join(creator_profile.get('topics_to_avoid', [])) or 'None'}

"""
        
        # Phase-specific instructions
        phase_instructions = self._get_phase_instructions(phase, previous_phases, user_message)
        
        return channel_info + top_video_info + recent_video_info + creator_info + phase_instructions

    def _get_phase_instructions(
        self, 
        phase: int, 
        previous_phases: Optional[Dict] = None,
        user_message: Optional[str] = None
    ) -> str:
        """Get phase-specific instructions"""
        
        phases = {
            1: """=== PHASE 1: CURRENT REALITY CHECK ===

Analyze and explain clearly:
1. What this channel is ACTUALLY about right now (based on content, not claims)
2. What type of content exists (formats, topics, styles)
3. What has relatively worked (highest engagement) and what hasn't
4. The gap between current content and likely creator goals

IMPORTANT: No advice yet. Only understanding and alignment.

Return your analysis as JSON:
{
    "channel_identity": "What this channel is actually about",
    "content_types": ["type1", "type2"],
    "what_works": [{"content": "description", "why_it_works": "reason"}],
    "what_doesnt_work": [{"content": "description", "why_it_fails": "reason"}],
    "performance_patterns": "Key patterns observed",
    "gap_analysis": "Gap between current state and growth potential",
    "summary": "2-3 sentence summary for the creator",
    "question_for_creator": "A specific question to understand their goals better"
}

End with asking if they want to continue to Phase 2 (Trend Analysis).""",

            2: f"""=== PHASE 2: TREND ANALYSIS (FILTERED) ===

Previous Analysis:
{json.dumps(previous_phases.get('phase_1', {}), indent=2) if previous_phases else 'Not available'}

{f'Creator response: {user_message}' if user_message else ''}

Identify 3-5 relevant trends ONLY within genres that fit this channel.
Focus on: format + topic + channel size relevance
Explain WHY these trends matter right now (February 2026).

Do NOT suggest actions yet.

Return as JSON:
{{
    "relevant_trends": [
        {{
            "trend_name": "Name of trend",
            "description": "What it is",
            "why_relevant": "Why it matters for THIS channel",
            "current_momentum": "rising/stable/declining",
            "channel_size_fit": "Why this fits their size",
            "examples": ["Example 1", "Example 2"]
        }}
    ],
    "trends_to_avoid": [
        {{
            "trend_name": "Name",
            "why_avoid": "Reason this doesn't fit"
        }}
    ],
    "summary": "Key insight for creator",
    "ready_for_phase_3": true
}}""",

            3: f"""=== PHASE 3: OPPORTUNITY MAPPING ===

Previous Phases:
Phase 1 (Reality Check): {json.dumps(previous_phases.get('phase_1', {}), indent=2) if previous_phases else 'N/A'}
Phase 2 (Trends): {json.dumps(previous_phases.get('phase_2', {}), indent=2) if previous_phases else 'N/A'}

{f'Creator response: {user_message}' if user_message else ''}

Analyze:
- Which trends fit THIS channel specifically
- Which trends are realistic given effort level
- Which trends should be avoided and why

Explain reasoning clearly.

Return as JSON:
{{
    "best_opportunities": [
        {{
            "opportunity": "Description",
            "fit_score": 85,
            "effort_required": "low/medium/high",
            "why_fits": "Specific reason for this channel",
            "potential_outcome": "What to expect",
            "time_to_results": "Estimated timeline"
        }}
    ],
    "avoid_list": [
        {{
            "opportunity": "What to avoid",
            "reason": "Why it doesn't fit"
        }}
    ],
    "priority_ranking": ["opportunity1", "opportunity2"],
    "summary": "Clear recommendation",
    "ready_for_phase_4": true
}}""",

            4: f"""=== PHASE 4: CONTENT IDEAS ===

CRITICAL RULE: Give ONLY ONE content idea in this response.

Previous Phases:
{json.dumps(previous_phases, indent=2) if previous_phases else 'N/A'}

{f'Creator response: {user_message}' if user_message else ''}

Create ONE specific content idea that:
1. Has current audience demand
2. Fits YouTube's current algorithm preferences
3. Matches this channel's size and history
4. Fits the creator's effort level
5. Has clear hook and simple payoff

Return as JSON:
{{
    "idea": {{
        "title": "Clear, compelling title",
        "concept": "What the video is about",
        "why_works_for_channel": "Specific reason",
        "why_now": "Trend + timing explanation",
        "format": "Short/Long",
        "suggested_duration": "Estimated length",
        "hook": "Opening hook (first 5 seconds)",
        "structure": ["Point 1", "Point 2", "Point 3"],
        "expected_outcome": "discoverability/retention/learning - NOT virality",
        "effort_level": "low/medium/high",
        "production_tips": ["tip1", "tip2"]
    }},
    "ask_creator": "Do you want another idea or should we refine this one?"
}}""",

            5: f"""=== PHASE 5: EXECUTION STRATEGY ===

Previous Phases and Ideas:
{json.dumps(previous_phases, indent=2) if previous_phases else 'N/A'}

{f'Creator response: {user_message}' if user_message else ''}

Now that ideas are accepted, provide:
- Posting frequency recommendation
- Content mix strategy
- Simple experimentation plan
- What to watch for in performance (signals, not numbers)

Return as JSON:
{{
    "posting_strategy": {{
        "frequency": "How often to post",
        "best_days": ["day1", "day2"],
        "best_times": "General timing advice",
        "reasoning": "Why this schedule"
    }},
    "content_mix": {{
        "ratio": "e.g., 70% main content, 20% shorts, 10% experimental",
        "explanation": "Why this mix"
    }},
    "experimentation_plan": [
        {{
            "experiment": "What to try",
            "duration": "How long",
            "success_signal": "What indicates it's working"
        }}
    ],
    "performance_signals": [
        {{
            "signal": "What to watch",
            "good_sign": "Positive indicator",
            "warning_sign": "Negative indicator"
        }}
    ],
    "summary": "Key execution advice",
    "ready_for_phase_6": true
}}""",

            6: f"""=== PHASE 6: LONG-TERM ROADMAP ===

All Previous Work:
{json.dumps(previous_phases, indent=2) if previous_phases else 'N/A'}

{f'Creator response: {user_message}' if user_message else ''}

Create a realistic roadmap focused on sustainability, not hacks.

Return as JSON:
{{
    "roadmap": {{
        "30_days": {{
            "focus": "Primary focus",
            "goals": ["goal1", "goal2"],
            "actions": ["action1", "action2"],
            "milestone": "What success looks like"
        }},
        "60_days": {{
            "focus": "Primary focus",
            "goals": ["goal1", "goal2"],
            "actions": ["action1", "action2"],
            "milestone": "What success looks like"
        }},
        "90_days": {{
            "focus": "Primary focus",
            "goals": ["goal1", "goal2"],
            "actions": ["action1", "action2"],
            "milestone": "What success looks like"
        }}
    }},
    "skill_improvements": [
        {{
            "skill": "Skill name",
            "why_important": "Reason",
            "how_to_improve": "Actionable steps"
        }}
    ],
    "positioning_strategy": {{
        "current_position": "Where you are now",
        "target_position": "Where you're heading",
        "differentiation": "What makes you unique"
    }},
    "sustainability_tips": ["tip1", "tip2", "tip3"],
    "final_advice": "Personalized closing guidance"
}}"""
        }
        
        return phases.get(phase, phases[1])

    def run_coaching_phase(
        self,
        phase: int,
        channel_metadata: Dict,
        top_videos: List[Dict],
        recent_videos: List[Dict],
        creator_profile: Optional[Dict] = None,
        previous_phases: Optional[Dict] = None,
        user_message: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Run a specific coaching phase
        
        Args:
            phase: Phase number (1-6)
            channel_metadata: Channel data
            top_videos: Top performing videos
            recent_videos: Recent videos
            creator_profile: Creator preferences
            previous_phases: Results from completed phases
            user_message: User's response/input
            
        Returns:
            Phase result as dictionary
        """
        try:
            prompt = self.prepare_phase_prompt(
                phase, channel_metadata, top_videos, recent_videos,
                creator_profile, previous_phases, user_message
            )
            
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4000,
                system_instruction=GROWTH_STRATEGIST_SYSTEM_PROMPT
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            response_text = response.text.strip()
            print(f"DEBUG: Phase {phase} response length: {len(response_text)}")
            
            # Extract JSON
            json_text = self._extract_json(response_text)
            
            result = json.loads(json_text)
            result['phase'] = phase
            result['model_version'] = self.model
            
            return result
            
        except Exception as e:
            print(f"Coaching phase {phase} error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_json(self, response_text: str) -> str:
        """Extract JSON from response text"""
        json_text = response_text
        
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            if json_end > json_start:
                json_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            newline_pos = response_text.find('\n', json_start)
            if newline_pos > json_start:
                json_start = newline_pos + 1
            json_end = response_text.find('```', json_start)
            if json_end > json_start:
                json_text = response_text[json_start:json_end].strip()
        
        if not json_text.startswith('{'):
            brace_start = json_text.find('{')
            brace_end = json_text.rfind('}') + 1
            if brace_start >= 0 and brace_end > brace_start:
                json_text = json_text[brace_start:brace_end]
        
        return json_text

    # ========== SIMPLE COACH METHODS ==========
    
    def generate_channel_summary(
        self,
        channel_data: Dict,
        videos: List[Dict]
    ) -> str:
        """
        Generate a concise channel summary for storage in DB.
        This summary will be used as context for chat interactions.
        """
        try:
            # Format channel data
            channel_info = f"""Channel: {channel_data.get('title', 'Unknown')}
Subscribers: {channel_data.get('subscriber_count', 0):,}
Total Videos: {channel_data.get('video_count', 0):,}
Total Views: {channel_data.get('view_count', 0):,}
Description: {channel_data.get('description', 'N/A')[:500]}
"""
            
            # Format video info
            video_info = "\nRecent Videos:\n"
            for idx, video in enumerate(videos[:10], 1):
                video_info += f"""
{idx}. "{video.get('title', 'Unknown')}"
   Views: {video.get('view_count', 0):,} | Likes: {video.get('like_count', 0):,}
   Duration: {video.get('duration', 'Unknown')}
"""
            
            prompt = f"""{channel_info}{video_info}

Create a comprehensive summary of this YouTube channel that captures:
1. What the channel is about (niche, topics, style)
2. Content patterns (video types, formats, frequency)
3. Performance insights (what's working, what's not)
4. Audience engagement patterns
5. Channel strengths and areas for improvement
6. Growth stage assessment (new, growing, established, stagnant)
7. Specific actionable recommendations for growth

Write this as a comprehensive summary (400-600 words) that includes specific details about:
- The channel's content niche and target audience
- Video performance patterns (views, engagement)
- What's working well and what needs improvement
- 3-5 specific, actionable growth strategies tailored to this channel

This summary will be used to provide personalized coaching advice, so be thorough and specific."""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2000
                )
            )
            
            summary = response.text.strip()
            print(f"📊 Gemini generated summary: {len(summary)} chars")
            return summary
            
        except Exception as e:
            print(f"❌ Channel summary generation error: {e}")
            return f"Channel: {channel_data.get('title', 'Unknown')} with {channel_data.get('subscriber_count', 0)} subscribers."

    def chat_with_context(
        self,
        channel_summary: str,
        channel_name: str,
        user_preferences: Dict,
        user_message: str
    ) -> str:
        """
        Generate a chat response using stored channel context.
        Acts as a YouTube growth coach answering user questions.
        """
        try:
            # Build context
            preferences_text = f"""
Creator Preferences:
- Preferred Genres: {', '.join(user_preferences.get('preferred_genres', [])) or 'Not specified'}
- Future Goals: {user_preferences.get('future_goals') or 'Not specified'}
- Effort Level: {user_preferences.get('effort_level', 'medium')}
- Editing Skills: {user_preferences.get('editing_skills', 'intermediate')}
- Current Challenges: {', '.join(user_preferences.get('current_challenges', [])) or 'None specified'}
"""
            
            system_context = f"""{GROWTH_STRATEGIST_SYSTEM_PROMPT}

=== CHANNEL CONTEXT ===
Channel Name: {channel_name}

{channel_summary}

{preferences_text}

=== END CONTEXT ===

You are having a conversation with this creator to help them grow their channel.

IMPORTANT GUIDELINES:
1. Give SPECIFIC, ACTIONABLE advice - not generic tips
2. Reference their actual channel data, video performance, and content style
3. Consider their goals ({user_preferences.get('future_goals', 'not specified')}) and constraints (effort: {user_preferences.get('effort_level', 'medium')}, skills: {user_preferences.get('editing_skills', 'intermediate')})
4. If they ask for solutions/ideas, give 3-5 concrete suggestions with brief explanations
5. Be encouraging but realistic about what's achievable
6. Keep responses focused and easy to act on (use bullet points for lists)
7. ALWAYS provide a COMPLETE response - never stop mid-sentence
8. Your response should be 200-400 words minimum with actionable details
"""

            prompt = f"""You are a YouTube growth coach helping the creator of "{channel_name}".

CHANNEL INFO:
{channel_summary[:1500] if len(channel_summary) > 1500 else channel_summary}

CREATOR PREFERENCES:
{preferences_text}

The creator asks: "{user_message}"

Give a helpful, detailed response with:
1. Direct answer to their question
2. At least 3 specific, actionable tips
3. Reference to their actual channel data when relevant

Be conversational but thorough. Write at least 300 words."""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=3000,
                    candidate_count=1
                )
            )
            
            chat_response = response.text.strip()
            print(f"💬 Chat response length: {len(chat_response)} chars")
            print(f"💬 Chat response preview: {chat_response[:200]}...")
            return chat_response
            
        except Exception as e:
            print(f"❌ Chat response error: {e}")
            return "I apologize, but I encountered an error processing your question. Please try again."

    # ========== END SIMPLE COACH METHODS ==========


# Global Gemini analyzer instance
gemini_analyzer = GeminiAnalyzer()
