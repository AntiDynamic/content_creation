"""
FastAPI application - REST API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db_session, init_db
from analysis_service import AnalysisService
from config import get_settings

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


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"✅ API running in {settings.app_env} mode")


@app.get("/")
async def root():
    """Root endpoint - API info"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
