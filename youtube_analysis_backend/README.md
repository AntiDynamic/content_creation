# YouTube Channel Analysis Backend

Production-ready backend service for analyzing YouTube channels using YouTube Data API and Gemini AI.

## 🚀 Features

- **Intelligent Channel Analysis**: AI-powered insights using Gemini 2.5 Flash
- **Multi-layer Caching**: Redis cache + PostgreSQL for optimal performance
- **Smart Video Sampling**: Analyzes representative videos (not all 10,000+)
- **Cost Optimized**: Context caching reduces API costs by 63%
- **Production Ready**: Proper error handling, rate limiting, monitoring

## 📋 Architecture

### Workflow Overview

1. **URL Validation** → Extract channel ID from various URL formats
2. **Cache Check** → Sub-100ms response for cached analyses
3. **Database Check** → Return existing analysis if fresh (< 30 days)
4. **YouTube API** → Fetch channel metadata and video list
5. **Smart Sampling** → Select 50 representative videos
6. **Gemini Analysis** → AI-powered content analysis
7. **Storage** → Save to database + cache
8. **Response** → Return structured analysis

### Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **APIs**: YouTube Data API v3, Gemini 2.5 Flash
- **Background Jobs**: Celery (optional)

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- YouTube Data API key
- Gemini API key

### Setup

1. **Clone and navigate to directory**
```bash
cd youtube_analysis_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

5. **Setup PostgreSQL database**
```bash
# Create database
createdb youtube_analysis

# Update DATABASE_URL in .env
# Example: postgresql://user:password@localhost:5432/youtube_analysis
```

6. **Start Redis**
```bash
# On Windows with WSL or Docker:
docker run -d -p 6379:6379 redis:latest

# Or install Redis locally
```

7. **Initialize database**
```bash
python -c "from database import init_db; init_db()"
```

## 🚀 Running the Application

### Development Mode

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/v1/docs`

## 📡 API Usage

### Analyze a Channel

**Endpoint**: `POST /v1/analyze`

**Request**:
```json
{
  "channel_url": "https://youtube.com/@mkbhd"
}
```

**Response**:
```json
{
  "channel": {
    "id": "UCBJycsmduvYEL83R_U4JriQ",
    "title": "Marques Brownlee",
    "subscriber_count": 18500000,
    "video_count": 1847,
    "thumbnail_url": "https://..."
  },
  "analysis": {
    "summary": "MKBHD is a technology-focused YouTube channel...",
    "themes": ["Technology Reviews", "Smartphones", "Consumer Electronics"],
    "target_audience": "Tech enthusiasts and consumers...",
    "content_style": "Professional, high-quality production...",
    "upload_frequency": "2-3 times per week"
  },
  "meta": {
    "analyzed_at": "2026-02-02T14:35:00Z",
    "videos_analyzed": 50,
    "total_videos": 1847,
    "freshness": "fresh",
    "confidence": 0.95,
    "model_version": "gemini-2.5-flash"
  }
}
```

### Get Existing Analysis

**Endpoint**: `GET /v1/channel/{channel_id}`

Returns cached or stored analysis without triggering new analysis.

### Health Check

**Endpoint**: `GET /health`

## 🔧 Configuration

Edit `.env` file:

```env
# API Keys
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/youtube_analysis

# Redis
REDIS_URL=redis://localhost:6379/0

# Analysis Settings
ANALYSIS_EXPIRY_DAYS=30
MAX_VIDEOS_TO_ANALYZE=50
ENABLE_CONTEXT_CACHING=true

# Gemini
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=1.0
```

## 📊 Performance Metrics

| Scenario | Response Time | API Cost |
|----------|--------------|----------|
| Cached result | < 100ms | $0 |
| Database result | < 500ms | $0 |
| Fresh analysis | 10-30s | ~$0.0013 |
| Re-analysis (with caching) | 10-30s | ~$0.0005 |

## 🔐 Rate Limiting

Default limits (configurable in `.env`):
- 10 new analyses per user per hour
- 20 requests per IP per hour

## 📈 Scaling Considerations

### Horizontal Scaling
- Run multiple API server instances behind load balancer
- Shared Redis cache across instances
- Database connection pooling

### Background Jobs
- Use Celery for async analysis processing
- Return job ID immediately, poll for results
- Better UX for 15-30 second processing time

### Monitoring
- Track YouTube API quota usage (10,000 units/day free)
- Monitor Gemini API costs
- Cache hit rate (target: >80%)

## 🐛 Troubleshooting

### YouTube API Quota Exceeded
- Free tier: 10,000 units/day
- Each new channel: ~52 units
- Capacity: ~192 new channels/day
- Solution: Implement user rate limiting, cache aggressively

### Database Connection Errors
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Check connection pool settings

### Redis Connection Errors
- Ensure Redis is running on port 6379
- Verify REDIS_URL in `.env`

### Gemini API Errors
- Verify GEMINI_API_KEY is correct
- Check API quota limits
- Review error logs for specific issues

## 📝 Project Structure

```
youtube_analysis_backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── models.py              # SQLAlchemy database models
├── database.py            # Database connection
├── cache.py               # Redis cache manager
├── youtube_service.py     # YouTube API client
├── gemini_service.py      # Gemini AI service
├── analysis_service.py    # Main orchestration logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🤝 Contributing

1. Follow the workflow design in `youtube_channel_analysis_workflow.md`
2. Maintain test coverage
3. Update documentation

## 📄 License

MIT License

## 🔗 Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
