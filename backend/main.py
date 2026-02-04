"""
FastAPI application - REST API endpoints
"""
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from database import get_db_session, init_db
from analysis_service import AnalysisService
from config import get_settings
from models import CreatorProfile, CoachingSession
from youtube_service import youtube_client
from gemini_service import gemini_analyzer as gemini_client

# Frontend directory
FRONTEND_DIR = Path(__file__).parent / "frontend"

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Channel Analysis API",
    description="Analyze YouTube channels using AI-powered insights",
    version=settings.api_version,
    docs_url=f"/{settings.api_version}/docs",
    redoc_url=f"/{settings.api_version}/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalyzeChannelRequest(BaseModel):
    """Request body for channel analysis"""
    channel_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_url": "https://youtube.com/@mkbhd"
            }
        }


class ChannelInfo(BaseModel):
    """Channel information"""
    id: str
    title: str
    subscriber_count: int
    video_count: int
    thumbnail_url: Optional[str] = None


class AnalysisResult(BaseModel):
    """Analysis results"""
    summary: str
    themes: list[str]
    target_audience: str
    content_style: str
    upload_frequency: str


class AnalysisMeta(BaseModel):
    """Analysis metadata"""
    analyzed_at: str
    videos_analyzed: int
    total_videos: int
    freshness: str
    confidence: float
    model_version: str


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    channel: ChannelInfo
    analysis: AnalysisResult
    meta: AnalysisMeta


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    error_code: str
    details: Optional[str] = None


class VideoInfo(BaseModel):
    """Video information for strategic analysis"""
    title: str
    views: int
    likes: int
    comments: int
    published_at: str
    thumbnail_url: Optional[str] = None


class ContentScore(BaseModel):
    """Content score breakdown"""
    overall: int
    consistency: int
    engagement: int
    growth_potential: int


class GrowthStrategy(BaseModel):
    """Growth strategy details"""
    priority: str
    action: str
    expected_impact: str
    timeline: str


class ContentRecommendation(BaseModel):
    """Content recommendation"""
    type: str
    description: str
    frequency: str
    example_topics: list[str]


class StrategicAnalysisResult(BaseModel):
    """Strategic analysis results"""
    strengths: list[str]
    weaknesses: list[str]
    growth_strategy: list[GrowthStrategy]
    content_recommendations: list[ContentRecommendation]
    thumbnail_advice: str
    title_advice: str
    upload_schedule: str
    engagement_tips: list[str]
    scores: ContentScore
    overall_verdict: str


class StrategicAnalysisResponse(BaseModel):
    """Complete strategic analysis response"""
    channel: ChannelInfo
    top_videos: list[VideoInfo]
    recent_videos: list[VideoInfo]
    analysis: StrategicAnalysisResult
    meta: AnalysisMeta


# Creator Profile Models
class CreatorProfileRequest(BaseModel):
    """Request body for creating/updating creator profile"""
    channel_url: str
    preferred_genres: List[str] = []
    future_goals: Optional[str] = None
    time_horizon: Optional[str] = None  # "30 days", "90 days", "6 months"
    effort_level: Optional[str] = None  # "low", "medium", "high"
    content_frequency: Optional[str] = None
    equipment_level: Optional[str] = None  # "basic", "intermediate", "professional"
    editing_skills: Optional[str] = None  # "beginner", "intermediate", "advanced"
    time_per_video: Optional[str] = None
    current_challenges: List[str] = []
    topics_to_avoid: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_url": "https://youtube.com/@example",
                "preferred_genres": ["tech reviews", "tutorials"],
                "future_goals": "Reach 100k subscribers and monetize",
                "time_horizon": "6 months",
                "effort_level": "medium",
                "content_frequency": "2 videos per week",
                "equipment_level": "intermediate",
                "editing_skills": "intermediate",
                "current_challenges": ["low views", "inconsistent uploads"],
                "topics_to_avoid": ["politics"]
            }
        }


class CreatorProfileResponse(BaseModel):
    """Response for creator profile"""
    channel_id: str
    preferred_genres: List[str]
    future_goals: Optional[str]
    time_horizon: Optional[str]
    effort_level: Optional[str]
    content_frequency: Optional[str]
    equipment_level: Optional[str]
    editing_skills: Optional[str]
    current_challenges: List[str]
    topics_to_avoid: List[str]


# Coaching Models
class StartCoachingRequest(BaseModel):
    """Request to start a coaching session"""
    channel_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_url": "https://youtube.com/@example"
            }
        }


class CoachingMessageRequest(BaseModel):
    """Request to continue coaching conversation"""
    session_id: str
    message: Optional[str] = None
    action: str = "continue"  # "continue", "refine", "another_idea", "skip"
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-uuid",
                "message": "Yes, continue to the next phase",
                "action": "continue"
            }
        }


class CoachingResponse(BaseModel):
    """Response from coaching session"""
    session_id: str
    current_phase: int
    phase_name: str
    response: dict
    completed_phases: List[int]
    next_action: str


# Simple Coach Models
class CoachSetupRequest(BaseModel):
    """Request for coach setup - profile + channel analysis"""
    channel_url: str
    preferred_genres: List[str] = []
    future_goals: Optional[str] = None
    effort_level: Optional[str] = "medium"
    editing_skills: Optional[str] = "intermediate"
    current_challenges: List[str] = []


class CoachChatRequest(BaseModel):
    """Request for coach chat"""
    channel_id: str
    message: str


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"✅ API running in {settings.app_env} mode")


# ========== SIMPLE COACH ENDPOINTS ==========

@app.post(f"/{settings.api_version}/coach/setup")
async def coach_setup(request: CoachSetupRequest, db: Session = Depends(get_db_session)):
    """
    Setup coaching profile - analyzes channel and stores summary in DB (hidden from user)
    """
    try:
        service = AnalysisService(db)
        
        # Get channel ID from URL
        channel_id = service._get_channel_id_from_url(request.channel_url)
        if not channel_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube channel URL")
        
        # Fetch channel data from YouTube
        channel_data = youtube_client.get_channel_metadata(channel_id)
        if not channel_data:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        # Fetch recent videos for analysis using upload playlist ID
        upload_playlist_id = channel_data.get('upload_playlist_id')
        video_list = youtube_client.get_channel_videos(upload_playlist_id, max_results=10) if upload_playlist_id else []
        
        # Get video details (views, likes, etc.)
        video_ids = [v['video_id'] for v in video_list]
        videos = youtube_client.get_video_details(video_ids) if video_ids else []
        
        # Generate channel summary using Gemini (stored in DB, not shown to user)
        channel_summary = gemini_client.generate_channel_summary(
            channel_data=channel_data,
            videos=videos
        )
        print(f"📝 Generated channel summary length: {len(channel_summary)} chars")
        print(f"📝 Summary preview: {channel_summary[:200]}...")
        
        # Check if profile exists
        profile = db.query(CreatorProfile).filter(CreatorProfile.channel_id == channel_id).first()
        
        if profile:
            # Update existing profile
            profile.channel_name = channel_data.get('title', '')
            profile.subscriber_count = channel_data.get('subscriber_count', 0)
            profile.video_count = channel_data.get('video_count', 0)
            profile.channel_summary = channel_summary
            profile.preferred_genres = request.preferred_genres
            profile.future_goals = request.future_goals
            profile.effort_level = request.effort_level
            profile.editing_skills = request.editing_skills
            profile.current_challenges = request.current_challenges
        else:
            # Create new profile
            profile = CreatorProfile(
                channel_id=channel_id,
                channel_name=channel_data.get('title', ''),
                subscriber_count=channel_data.get('subscriber_count', 0),
                video_count=channel_data.get('video_count', 0),
                channel_summary=channel_summary,
                preferred_genres=request.preferred_genres,
                future_goals=request.future_goals,
                effort_level=request.effort_level,
                editing_skills=request.editing_skills,
                current_challenges=request.current_challenges
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "channel_name": channel_data.get('title', ''),
            "profile_id": profile.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Coach setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"/{settings.api_version}/coach/chat")
async def coach_chat(request: CoachChatRequest, db: Session = Depends(get_db_session)):
    """
    Chat with the coach - uses stored channel summary for context
    """
    try:
        # Get profile with stored summary
        profile = db.query(CreatorProfile).filter(
            CreatorProfile.channel_id == request.channel_id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please complete setup first.")
        
        if not profile.channel_summary:
            raise HTTPException(status_code=400, detail="Channel analysis not available. Please redo setup.")
        
        # Generate chat response using stored context
        response = gemini_client.chat_with_context(
            channel_summary=profile.channel_summary,
            channel_name=profile.channel_name,
            user_preferences={
                "preferred_genres": profile.preferred_genres,
                "future_goals": profile.future_goals,
                "effort_level": profile.effort_level,
                "editing_skills": profile.editing_skills,
                "current_challenges": profile.current_challenges
            },
            user_message=request.message
        )
        
        return {
            "success": True,
            "response": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Coach chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== END SIMPLE COACH ENDPOINTS ==========


@app.get("/api")
async def api_info():
    """API info endpoint"""
    return {
        "service": "YouTube Channel Analysis API",
        "version": settings.api_version,
        "status": "operational",
        "docs": f"/{settings.api_version}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


@app.post(
    f"/{settings.api_version}/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Channel not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_channel(
    request: AnalyzeChannelRequest,
    db: Session = Depends(get_db_session)
):
    """
    Analyze a YouTube channel
    
    This endpoint accepts a YouTube channel URL and returns a comprehensive
    AI-generated analysis of the channel's content, themes, and audience.
    
    **Workflow:**
    1. Validates and extracts channel ID from URL
    2. Checks cache and database for existing analysis
    3. If not found or expired, fetches fresh data from YouTube
    4. Analyzes content using Gemini AI
    5. Stores results and returns analysis
    
    **Response time:**
    - Cached: < 100ms
    - Database: < 500ms
    - Fresh analysis: 10-30 seconds
    
    **Supported URL formats:**
    - `https://youtube.com/@username`
    - `https://youtube.com/channel/UC123...`
    - `https://youtube.com/c/channelname`
    - `https://youtube.com/user/username`
    """
    try:
        # Create analysis service
        service = AnalysisService(db)
        
        # Run analysis
        result = service.analyze_channel(request.channel_url)
        
        # Handle errors
        if not result['success']:
            error_code = result.get('error_code', 'UNKNOWN_ERROR')
            error_message = result.get('error', 'An error occurred')
            
            if error_code == 'INVALID_URL':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
            elif error_code == 'CHANNEL_NOT_FOUND':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
        
        # Return successful response
        return result['data']
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_channel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": str(e) if settings.debug else None
            }
        )


@app.post(
    f"/{settings.api_version}/analyze/strategic",
    response_model=StrategicAnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Channel not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_channel_strategic(
    request: AnalyzeChannelRequest,
    db: Session = Depends(get_db_session)
):
    """
    Strategic YouTube Channel Analysis
    
    This endpoint provides deep strategic guidance by analyzing:
    - Top 5 most viewed videos (what works best)
    - Latest 5 videos (current direction)
    
    **Returns comprehensive guidance including:**
    - Strengths and weaknesses analysis
    - Growth strategies with priorities and timelines
    - Content recommendations with example topics
    - Thumbnail and title optimization advice
    - Upload schedule recommendations
    - Engagement improvement tips
    - Content scores (overall, consistency, engagement, growth potential)
    
    **Response time:** 15-45 seconds (depending on AI analysis)
    """
    try:
        # Create analysis service
        service = AnalysisService(db)
        
        # Run strategic analysis
        result = service.analyze_channel_strategic(request.channel_url)
        
        # Handle errors
        if not result.get('success', False):
            error_code = result.get('error_code', 'UNKNOWN_ERROR')
            error_message = result.get('error', 'An error occurred')
            
            if error_code == 'INVALID_URL':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
            elif error_code == 'CHANNEL_NOT_FOUND':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": error_message,
                        "error_code": error_code
                    }
                )
        
        # Return successful response
        return result['data']
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_channel_strategic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": str(e) if settings.debug else None
            }
        )


@app.get(f"/{settings.api_version}/channel/{{channel_id}}")
async def get_channel_analysis(
    channel_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get existing analysis for a channel by ID
    
    Returns cached or database-stored analysis if available.
    Does not trigger a new analysis.
    """
    from cache import cache
    from models import ChannelAnalysis
    
    # Check cache
    cached = cache.get_channel_analysis(channel_id)
    if cached:
        return {
            "success": True,
            "data": cached,
            "source": "cache"
        }
    
    # Check database
    analysis = db.query(ChannelAnalysis).filter(
        ChannelAnalysis.channel_id == channel_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "No analysis found for this channel",
                "error_code": "NOT_FOUND"
            }
        )
    
    # Format response
    from analysis_service import AnalysisService
    from models import Channel
    
    channel = db.query(Channel).filter(Channel.channel_id == channel_id).first()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Channel metadata not found",
                "error_code": "CHANNEL_NOT_FOUND"
            }
        )
    
    channel_metadata = {
        'channel_id': channel.channel_id,
        'title': channel.title,
        'subscriber_count': channel.subscriber_count,
        'video_count': channel.video_count,
        'thumbnail_url': channel.thumbnail_url
    }
    
    service = AnalysisService(db)
    response_data = service._format_analysis_response(channel_metadata, analysis)
    
    return {
        "success": True,
        "data": response_data,
        "source": "database"
    }


# ================== CREATOR PROFILE ENDPOINTS ==================

@app.post(f"/{settings.api_version}/profile")
async def create_or_update_profile(
    request: CreatorProfileRequest,
    db: Session = Depends(get_db_session)
):
    """
    Create or update a creator profile
    
    This stores the creator's preferences and goals for personalized coaching.
    """
    try:
        service = AnalysisService(db)
        channel_id = service._get_channel_id_from_url(request.channel_url)
        
        if not channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid YouTube URL", "error_code": "INVALID_URL"}
            )
        
        # Check if profile exists
        existing = db.query(CreatorProfile).filter(
            CreatorProfile.channel_id == channel_id
        ).first()
        
        if existing:
            # Update existing profile
            existing.preferred_genres = request.preferred_genres
            existing.future_goals = request.future_goals
            existing.time_horizon = request.time_horizon
            existing.effort_level = request.effort_level
            existing.content_frequency = request.content_frequency
            existing.equipment_level = request.equipment_level
            existing.editing_skills = request.editing_skills
            existing.current_challenges = request.current_challenges
            existing.topics_to_avoid = request.topics_to_avoid
            db.commit()
            profile = existing
        else:
            # Create new profile
            profile = CreatorProfile(
                channel_id=channel_id,
                preferred_genres=request.preferred_genres,
                future_goals=request.future_goals,
                time_horizon=request.time_horizon,
                effort_level=request.effort_level,
                content_frequency=request.content_frequency,
                equipment_level=request.equipment_level,
                editing_skills=request.editing_skills,
                current_challenges=request.current_challenges,
                topics_to_avoid=request.topics_to_avoid
            )
            db.add(profile)
            db.commit()
        
        return {
            "success": True,
            "message": "Profile saved successfully",
            "data": {
                "channel_id": profile.channel_id,
                "preferred_genres": profile.preferred_genres,
                "future_goals": profile.future_goals,
                "time_horizon": profile.time_horizon,
                "effort_level": profile.effort_level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to save profile", "error_code": "PROFILE_ERROR"}
        )


@app.get(f"/{settings.api_version}/profile/{{channel_id}}")
async def get_profile(
    channel_id: str,
    db: Session = Depends(get_db_session)
):
    """Get creator profile by channel ID"""
    profile = db.query(CreatorProfile).filter(
        CreatorProfile.channel_id == channel_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Profile not found", "error_code": "NOT_FOUND"}
        )
    
    return {
        "success": True,
        "data": {
            "channel_id": profile.channel_id,
            "preferred_genres": profile.preferred_genres or [],
            "future_goals": profile.future_goals,
            "time_horizon": profile.time_horizon,
            "effort_level": profile.effort_level,
            "content_frequency": profile.content_frequency,
            "equipment_level": profile.equipment_level,
            "editing_skills": profile.editing_skills,
            "current_challenges": profile.current_challenges or [],
            "topics_to_avoid": profile.topics_to_avoid or [],
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
    }


# ================== COACHING ENDPOINTS ==================

PHASE_NAMES = {
    1: "Current Reality Check",
    2: "Trend Analysis",
    3: "Opportunity Mapping",
    4: "Content Ideas",
    5: "Execution Strategy",
    6: "Long-Term Roadmap"
}


@app.post(f"/{settings.api_version}/coaching/start")
async def start_coaching_session(
    request: StartCoachingRequest,
    db: Session = Depends(get_db_session)
):
    """
    Start a new coaching session
    
    This initiates Phase 1 (Current Reality Check) and returns the analysis.
    The session is saved for continuation.
    """
    try:
        from gemini_service import gemini_analyzer
        from youtube_service import youtube_client
        from datetime import datetime
        
        service = AnalysisService(db)
        channel_id = service._get_channel_id_from_url(request.channel_url)
        
        if not channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid YouTube URL", "error_code": "INVALID_URL"}
            )
        
        # Fetch channel data using the service's internal method
        channel_metadata = service._fetch_and_store_channel_metadata(channel_id)
        if not channel_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Channel not found", "error_code": "CHANNEL_NOT_FOUND"}
            )
        
        # Fetch video list
        videos_list = service._fetch_video_list(channel_metadata.get('upload_playlist_id'))
        if not videos_list:
            top_videos = []
            recent_videos = []
        else:
            # Get details for up to 50 videos
            video_ids = [v['video_id'] for v in videos_list[:50]]
            all_videos = youtube_client.get_video_details(video_ids)
            
            # Sort for top and recent
            sorted_by_views = sorted(all_videos, key=lambda x: x.get('view_count', 0), reverse=True)
            sorted_by_date = sorted(all_videos, key=lambda x: x.get('published_at', ''), reverse=True)
            
            top_videos = sorted_by_views[:5]
            recent_videos = sorted_by_date[:5]
        
        # Get creator profile if exists
        profile = db.query(CreatorProfile).filter(
            CreatorProfile.channel_id == channel_id
        ).first()
        
        creator_profile = None
        if profile:
            creator_profile = {
                "preferred_genres": profile.preferred_genres or [],
                "future_goals": profile.future_goals,
                "time_horizon": profile.time_horizon,
                "effort_level": profile.effort_level,
                "content_frequency": profile.content_frequency,
                "equipment_level": profile.equipment_level,
                "editing_skills": profile.editing_skills,
                "current_challenges": profile.current_challenges or [],
                "topics_to_avoid": profile.topics_to_avoid or []
            }
        
        # Run Phase 1
        phase_result = gemini_analyzer.run_coaching_phase(
            phase=1,
            channel_metadata=channel_metadata,
            top_videos=top_videos,
            recent_videos=recent_videos,
            creator_profile=creator_profile
        )
        
        if not phase_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "AI analysis failed", "error_code": "AI_ERROR"}
            )
        
        # Create session
        session_id = str(uuid.uuid4())
        session = CoachingSession(
            session_id=session_id,
            channel_id=channel_id,
            current_phase=1,
            phase_1_completed=True,
            phase_1_result=phase_result,
            conversation_history=[{
                "phase": 1,
                "timestamp": datetime.utcnow().isoformat(),
                "result": phase_result
            }]
        )
        db.add(session)
        db.commit()
        
        return {
            "success": True,
            "session_id": session_id,
            "current_phase": 1,
            "phase_name": PHASE_NAMES[1],
            "response": phase_result,
            "completed_phases": [1],
            "next_action": "Reply with your thoughts or say 'continue' to move to Phase 2 (Trend Analysis)",
            "channel": {
                "id": channel_id,
                "title": channel_metadata.get('title'),
                "subscribers": channel_metadata.get('subscriber_count', 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting coaching: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "error_code": "COACHING_ERROR"}
        )


@app.post(f"/{settings.api_version}/coaching/continue")
async def continue_coaching_session(
    request: CoachingMessageRequest,
    db: Session = Depends(get_db_session)
):
    """
    Continue an existing coaching session
    
    Actions:
    - "continue": Move to next phase
    - "refine": Refine current phase based on feedback
    - "another_idea": (Phase 4 only) Generate another content idea
    - "skip": Skip to a specific phase
    """
    try:
        from gemini_service import gemini_analyzer
        from youtube_service import youtube_client
        from datetime import datetime
        
        # Get session
        session = db.query(CoachingSession).filter(
            CoachingSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Session not found", "error_code": "SESSION_NOT_FOUND"}
            )
        
        channel_id = session.channel_id
        current_phase = session.current_phase
        
        # Determine next phase
        if request.action == "continue":
            next_phase = min(current_phase + 1, 6)
        elif request.action == "another_idea" and current_phase == 4:
            next_phase = 4  # Stay on phase 4 for more ideas
        elif request.action == "refine":
            next_phase = current_phase  # Refine current phase
        else:
            next_phase = current_phase + 1
        
        # Check if already completed all phases
        if current_phase == 6 and session.phase_6_completed and request.action == "continue":
            return {
                "success": True,
                "session_id": session.session_id,
                "current_phase": 6,
                "phase_name": "Completed",
                "response": {"message": "All phases completed! Review your roadmap and start executing."},
                "completed_phases": [1, 2, 3, 4, 5, 6],
                "next_action": "Start implementing your strategy!"
            }
        
        # Fetch channel data using service
        service = AnalysisService(db)
        channel_metadata = service._fetch_and_store_channel_metadata(channel_id)
        
        # Fetch videos
        top_videos = []
        recent_videos = []
        if channel_metadata:
            videos_list = service._fetch_video_list(channel_metadata.get('upload_playlist_id'))
            if videos_list:
                video_ids = [v['video_id'] for v in videos_list[:50]]
                all_videos = youtube_client.get_video_details(video_ids)
                
                sorted_by_views = sorted(all_videos, key=lambda x: x.get('view_count', 0), reverse=True)
                sorted_by_date = sorted(all_videos, key=lambda x: x.get('published_at', ''), reverse=True)
                
                top_videos = sorted_by_views[:5]
                recent_videos = sorted_by_date[:5]
        
        # Get creator profile
        profile = db.query(CreatorProfile).filter(
            CreatorProfile.channel_id == channel_id
        ).first()
        
        creator_profile = None
        if profile:
            creator_profile = {
                "preferred_genres": profile.preferred_genres or [],
                "future_goals": profile.future_goals,
                "time_horizon": profile.time_horizon,
                "effort_level": profile.effort_level,
                "content_frequency": profile.content_frequency,
                "equipment_level": profile.equipment_level,
                "editing_skills": profile.editing_skills,
                "current_challenges": profile.current_challenges or [],
                "topics_to_avoid": profile.topics_to_avoid or []
            }
        
        # Gather previous phases
        previous_phases = {}
        if session.phase_1_result:
            previous_phases['phase_1'] = session.phase_1_result
        if session.phase_2_result:
            previous_phases['phase_2'] = session.phase_2_result
        if session.phase_3_result:
            previous_phases['phase_3'] = session.phase_3_result
        if session.phase_4_result:
            previous_phases['phase_4'] = session.phase_4_result
        if session.phase_5_result:
            previous_phases['phase_5'] = session.phase_5_result
        
        # Run next phase
        phase_result = gemini_analyzer.run_coaching_phase(
            phase=next_phase,
            channel_metadata=channel_metadata,
            top_videos=top_videos,
            recent_videos=recent_videos,
            creator_profile=creator_profile,
            previous_phases=previous_phases,
            user_message=request.message
        )
        
        if not phase_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "AI analysis failed", "error_code": "AI_ERROR"}
            )
        
        # Update session
        session.current_phase = next_phase
        session.last_interaction = datetime.utcnow()
        
        # Store phase result
        if next_phase == 1:
            session.phase_1_result = phase_result
            session.phase_1_completed = True
        elif next_phase == 2:
            session.phase_2_result = phase_result
            session.phase_2_completed = True
        elif next_phase == 3:
            session.phase_3_result = phase_result
            session.phase_3_completed = True
        elif next_phase == 4:
            # For phase 4, accumulate ideas
            if session.phase_4_result and isinstance(session.phase_4_result, list):
                session.phase_4_result = session.phase_4_result + [phase_result]
            elif session.phase_4_result:
                session.phase_4_result = [session.phase_4_result, phase_result]
            else:
                session.phase_4_result = [phase_result]
            session.phase_4_completed = True
        elif next_phase == 5:
            session.phase_5_result = phase_result
            session.phase_5_completed = True
        elif next_phase == 6:
            session.phase_6_result = phase_result
            session.phase_6_completed = True
        
        # Update conversation history
        history = session.conversation_history or []
        history.append({
            "phase": next_phase,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": request.message,
            "result": phase_result
        })
        session.conversation_history = history
        
        db.commit()
        
        # Build completed phases list
        completed = []
        if session.phase_1_completed: completed.append(1)
        if session.phase_2_completed: completed.append(2)
        if session.phase_3_completed: completed.append(3)
        if session.phase_4_completed: completed.append(4)
        if session.phase_5_completed: completed.append(5)
        if session.phase_6_completed: completed.append(6)
        
        # Determine next action message
        if next_phase < 6:
            next_action = f"Reply with feedback or say 'continue' to move to Phase {next_phase + 1} ({PHASE_NAMES[next_phase + 1]})"
        elif next_phase == 4:
            next_action = "Say 'continue' for Execution Strategy, 'another_idea' for more ideas, or provide feedback"
        else:
            next_action = "Coaching complete! Start implementing your roadmap."
        
        return {
            "success": True,
            "session_id": session.session_id,
            "current_phase": next_phase,
            "phase_name": PHASE_NAMES[next_phase],
            "response": phase_result,
            "completed_phases": completed,
            "next_action": next_action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error continuing coaching: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "error_code": "COACHING_ERROR"}
        )


@app.get(f"/{settings.api_version}/coaching/session/{{session_id}}")
async def get_coaching_session(
    session_id: str,
    db: Session = Depends(get_db_session)
):
    """Get coaching session details and history"""
    session = db.query(CoachingSession).filter(
        CoachingSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Session not found", "error_code": "SESSION_NOT_FOUND"}
        )
    
    completed = []
    if session.phase_1_completed: completed.append(1)
    if session.phase_2_completed: completed.append(2)
    if session.phase_3_completed: completed.append(3)
    if session.phase_4_completed: completed.append(4)
    if session.phase_5_completed: completed.append(5)
    if session.phase_6_completed: completed.append(6)
    
    return {
        "success": True,
        "data": {
            "session_id": session.session_id,
            "channel_id": session.channel_id,
            "current_phase": session.current_phase,
            "phase_name": PHASE_NAMES.get(session.current_phase, "Unknown"),
            "completed_phases": completed,
            "phases": {
                "phase_1": session.phase_1_result,
                "phase_2": session.phase_2_result,
                "phase_3": session.phase_3_result,
                "phase_4": session.phase_4_result,
                "phase_5": session.phase_5_result,
                "phase_6": session.phase_6_result
            },
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "last_interaction": session.last_interaction.isoformat() if session.last_interaction else None
        }
    }


@app.get(f"/{settings.api_version}/coaching/sessions/{{channel_id}}")
async def get_channel_coaching_sessions(
    channel_id: str,
    db: Session = Depends(get_db_session)
):
    """Get all coaching sessions for a channel"""
    sessions = db.query(CoachingSession).filter(
        CoachingSession.channel_id == channel_id
    ).order_by(CoachingSession.created_at.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "session_id": s.session_id,
                "current_phase": s.current_phase,
                "phase_name": PHASE_NAMES.get(s.current_phase, "Unknown"),
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "last_interaction": s.last_interaction.isoformat() if s.last_interaction else None
            }
            for s in sessions
        ]
    }


# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    return FileResponse(FRONTEND_DIR / "index.html")

# Mount static files (CSS, JS) - must be after API routes
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
