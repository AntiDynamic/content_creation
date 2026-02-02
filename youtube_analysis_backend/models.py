"""
SQLAlchemy database models for YouTube Analysis Backend
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Channel(Base):
    """Channel metadata from YouTube"""
    __tablename__ = "channels"
    
    channel_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subscriber_count = Column(Integer)
    video_count = Column(Integer)
    view_count = Column(Integer)
    upload_playlist_id = Column(String(50))
    published_at = Column(DateTime)
    country = Column(String(10))
    custom_url = Column(String(255))
    thumbnail_url = Column(String(500))
    
    # Metadata
    fetched_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Channel(channel_id='{self.channel_id}', title='{self.title}')>"


class Video(Base):
    """Video metadata from YouTube"""
    __tablename__ = "videos"
    
    video_id = Column(String(20), primary_key=True, index=True)
    channel_id = Column(String(50), index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, index=True)
    duration = Column(String(20))
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    tags = Column(JSON)  # Array of tags
    category_id = Column(String(10))
    
    # Metadata
    fetched_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_channel_published', 'channel_id', 'published_at'),
        Index('idx_channel_views', 'channel_id', 'view_count'),
    )
    
    def __repr__(self):
        return f"<Video(video_id='{self.video_id}', title='{self.title[:30]}...')>"


class ChannelAnalysis(Base):
    """AI-generated channel analysis results"""
    __tablename__ = "channel_analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(50), index=True, nullable=False, unique=True)
    
    # Analysis Results
    summary = Column(Text, nullable=False)
    themes = Column(JSON)  # Array of themes
    target_audience = Column(Text)
    content_style = Column(Text)
    upload_frequency = Column(String(100))
    
    # Analysis Metadata
    analyzed_videos_count = Column(Integer, nullable=False)
    total_videos_count = Column(Integer, nullable=False)
    confidence_score = Column(Float)
    model_version = Column(String(50))  # e.g., "gemini-2.5-flash"
    
    # Timestamps
    analyzed_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Video sample used for analysis (for reproducibility)
    video_sample_ids = Column(JSON)  # Array of video IDs
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.expires_at and self.analyzed_at:
            from config import get_settings
            settings = get_settings()
            self.expires_at = self.analyzed_at + timedelta(days=settings.analysis_expiry_days)
    
    @property
    def is_expired(self) -> bool:
        """Check if analysis has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def freshness(self) -> str:
        """Get freshness status"""
        if self.is_expired:
            return "stale"
        days_old = (datetime.utcnow() - self.analyzed_at).days
        if days_old < 7:
            return "fresh"
        elif days_old < 14:
            return "recent"
        else:
            return "aging"
    
    def __repr__(self):
        return f"<ChannelAnalysis(channel_id='{self.channel_id}', analyzed_at='{self.analyzed_at}')>"


class AnalysisJob(Base):
    """Track background analysis jobs"""
    __tablename__ = "analysis_jobs"
    
    job_id = Column(String(50), primary_key=True)
    channel_id = Column(String(50), index=True, nullable=False)
    status = Column(String(20), nullable=False, index=True)  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Result reference
    analysis_id = Column(Integer)  # FK to channel_analyses.id
    
    def __repr__(self):
        return f"<AnalysisJob(job_id='{self.job_id}', status='{self.status}')>"
