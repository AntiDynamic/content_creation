"""
Configuration management for YouTube Analysis Backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    youtube_api_key: str
    gemini_api_key: str
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis (optional for development)
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50
    
    # Cache TTL (seconds)
    cache_ttl_channel_analysis: int = 604800  # 7 days
    cache_ttl_channel_metadata: int = 604800  # 7 days
    cache_ttl_video_transcript: int = 7776000  # 90 days
    cache_ttl_url_mapping: int = 86400  # 24 hours
    
    # Analysis Settings
    analysis_expiry_days: int = 30
    max_videos_to_analyze: int = 50
    enable_transcripts: bool = False
    
    # Gemini Configuration
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 1.0
    gemini_max_output_tokens: int = 1000
    enable_context_caching: bool = True
    
    # Rate Limiting
    rate_limit_per_user_hour: int = 10
    rate_limit_per_ip_hour: int = 20
    
    # Background Jobs
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Application
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_version: str = "v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


from pathlib import Path

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    # Try to find .env file in the script's directory
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    
    if env_file.exists():
        return Settings(_env_file=str(env_file))
    return Settings()
