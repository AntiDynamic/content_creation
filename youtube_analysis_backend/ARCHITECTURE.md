# 📊 System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                           │
│                    (YouTube Channel URL)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                         │
│                     (main.py - Port 8000)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS SERVICE                              │
│                  (analysis_service.py)                           │
│                                                                   │
│  Orchestrates the complete workflow:                             │
│  1. URL validation                                               │
│  2. Cache/DB check                                               │
│  3. YouTube API calls                                            │
│  4. Gemini AI analysis                                           │
│  5. Storage & response                                           │
└──────┬──────────────┬──────────────┬──────────────┬─────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  CACHE   │  │ DATABASE │  │ YOUTUBE  │  │  GEMINI  │
│  LAYER   │  │  LAYER   │  │   API    │  │   API    │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Data Flow Diagram

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│ 1. Extract Channel ID from URL          │
│    • Parse URL format                   │
│    • Check cache for URL→ID mapping     │
│    • Resolve @handle if needed          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. Check Existing Analysis              │
│    ┌─────────────────────────────────┐  │
│    │ Redis Cache (< 100ms)           │  │
│    │ Key: channel_analysis:{id}      │  │
│    └──────────┬──────────────────────┘  │
│               │ MISS                     │
│    ┌──────────▼──────────────────────┐  │
│    │ PostgreSQL Database (< 500ms)   │  │
│    │ Table: channel_analyses         │  │
│    │ Filter: NOT expired             │  │
│    └──────────┬──────────────────────┘  │
│               │ MISS                     │
└───────────────┼──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ 3. Fetch Channel Metadata               │
│    • YouTube API: channels.list         │
│    • Cost: 1 quota unit                 │
│    • Store in DB + Cache                │
│    • Extract upload_playlist_id         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 4. Fetch Video List                     │
│    • YouTube API: playlistItems.list    │
│    • Pagination: 50 videos/request      │
│    • Cost: 1 unit per 50 videos         │
│    • Max fetch: 500 videos              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 5. Intelligent Video Sampling           │
│    Strategy based on channel size:      │
│    • < 50 videos: Use all               │
│    • 50-500: Recent 30 + distributed 20 │
│    • 500+: Recent 25 + distributed 25   │
│    • Max sample: 50 videos              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 6. Fetch Detailed Video Data            │
│    • YouTube API: videos.list           │
│    • Batch: 50 videos per request       │
│    • Cost: 1 quota unit                 │
│    • Data: title, desc, stats, tags     │
│    • Store in DB: videos table          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 7. Prepare Gemini Prompt                │
│    • Channel metadata (~500 tokens)     │
│    • 50 videos × 300 tokens = 15K       │
│    • Instructions (~200 tokens)         │
│    • Total: ~15,700 tokens              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 8. Gemini AI Analysis                   │
│    • Model: gemini-2.5-flash            │
│    • Temperature: 1.0                   │
│    • Max output: 1000 tokens            │
│    • Context caching: ENABLED           │
│    • Cost: $0.0013 (first)              │
│    •       $0.0005 (cached)             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 9. Parse & Validate Response            │
│    • Extract JSON from response         │
│    • Validate required fields           │
│    • Add metadata                       │
│    • Calculate confidence score         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 10. Store Analysis Results              │
│    ┌─────────────────────────────────┐  │
│    │ PostgreSQL (Permanent)          │  │
│    │ Table: channel_analyses         │  │
│    │ Expires: analyzed_at + 30 days  │  │
│    └─────────────────────────────────┘  │
│    ┌─────────────────────────────────┐  │
│    │ Redis Cache (Fast Access)       │  │
│    │ TTL: 7 days                     │  │
│    │ Key: channel_analysis:{id}      │  │
│    └─────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 11. Return Response                     │
│    • Channel info                       │
│    • Analysis (summary, themes, etc)    │
│    • Metadata (freshness, confidence)   │
│    • HTTP 200 OK                        │
└─────────────────────────────────────────┘
```

## Cache Strategy

```
┌──────────────────────────────────────────────────────────┐
│                    CACHE HIERARCHY                        │
└──────────────────────────────────────────────────────────┘

Layer 1: Redis Cache (In-Memory, Fast)
┌────────────────────────────────────────────────────────┐
│ channel_analysis:{id}     TTL: 7 days                  │
│ channel_meta:{id}         TTL: 7 days                  │
│ channel_url:{hash}        TTL: 24 hours                │
│ video_transcript:{id}     TTL: 90 days                 │
└────────────────────────────────────────────────────────┘
                           │
                           │ Cache Miss
                           ▼
Layer 2: PostgreSQL Database (Persistent, Slower)
┌────────────────────────────────────────────────────────┐
│ channels                  Permanent                     │
│ videos                    Permanent                     │
│ channel_analyses          Expires after 30 days        │
│ analysis_jobs             Permanent (for tracking)     │
└────────────────────────────────────────────────────────┘
                           │
                           │ Not Found or Expired
                           ▼
Layer 3: External APIs (Slowest, Costs Money)
┌────────────────────────────────────────────────────────┐
│ YouTube Data API          Quota: 10K units/day         │
│ Gemini AI API             Cost: ~$0.0013/channel       │
└────────────────────────────────────────────────────────┘
```

## Database Schema

```sql
-- Channels table
CREATE TABLE channels (
    channel_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subscriber_count INTEGER,
    video_count INTEGER,
    view_count INTEGER,
    upload_playlist_id VARCHAR(50),
    published_at TIMESTAMP,
    country VARCHAR(10),
    custom_url VARCHAR(255),
    thumbnail_url VARCHAR(500),
    fetched_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Videos table
CREATE TABLE videos (
    video_id VARCHAR(20) PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    published_at TIMESTAMP,
    duration VARCHAR(20),
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    tags JSON,
    category_id VARCHAR(10),
    fetched_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_channel_published (channel_id, published_at),
    INDEX idx_channel_views (channel_id, view_count)
);

-- Channel analyses table
CREATE TABLE channel_analyses (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    channel_id VARCHAR(50) UNIQUE NOT NULL,
    summary TEXT NOT NULL,
    themes JSON,
    target_audience TEXT,
    content_style TEXT,
    upload_frequency VARCHAR(100),
    analyzed_videos_count INTEGER NOT NULL,
    total_videos_count INTEGER NOT NULL,
    confidence_score FLOAT,
    model_version VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    video_sample_ids JSON,
    
    INDEX idx_channel (channel_id),
    INDEX idx_analyzed_at (analyzed_at),
    INDEX idx_expires_at (expires_at)
);

-- Analysis jobs table (for async processing)
CREATE TABLE analysis_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    analysis_id INTEGER,
    
    INDEX idx_channel (channel_id),
    INDEX idx_status (status)
);
```

## API Endpoints

```
┌─────────────────────────────────────────────────────────────┐
│                      API ENDPOINTS                           │
└─────────────────────────────────────────────────────────────┘

POST /v1/analyze
├─ Description: Analyze a YouTube channel
├─ Request: { "channel_url": "https://youtube.com/@channel" }
├─ Response: Full analysis with channel info and AI insights
├─ Status: 200 OK, 400 Bad Request, 404 Not Found, 500 Error
└─ Time: 10-30s (fresh), <100ms (cached)

GET /v1/channel/{channel_id}
├─ Description: Get existing analysis by channel ID
├─ Response: Cached or stored analysis
├─ Status: 200 OK, 404 Not Found
└─ Time: <500ms

GET /health
├─ Description: Health check endpoint
├─ Response: { "status": "healthy" }
└─ Time: <10ms

GET /
├─ Description: API information
└─ Response: Service info and docs link
```

## Performance Characteristics

```
┌────────────────────────────────────────────────────────┐
│              PERFORMANCE METRICS                        │
└────────────────────────────────────────────────────────┘

Response Times:
├─ Cache Hit (Redis)           < 100ms    ████░░░░░░
├─ Database Hit                < 500ms    ██████░░░░
├─ Fresh Analysis (Small)      10-15s     ██████████
└─ Fresh Analysis (Large)      20-30s     ██████████

API Costs (per channel):
├─ First Analysis              $0.0013
├─ Re-analysis (cached)        $0.0005
└─ Cached Response             $0.0000

YouTube API Quota:
├─ Daily Limit                 10,000 units
├─ Per Channel                 ~52 units
├─ Daily Capacity              ~192 new channels
└─ With Caching                Unlimited repeats

Database Storage:
├─ Channel Metadata            ~2 KB
├─ Video Metadata (50)         ~25 KB
├─ Analysis Result             ~5 KB
└─ Total per Channel           ~32 KB
```

## Error Handling Flow

```
Request → Validation → Processing → Response
   │           │            │           │
   │           │            │           ├─ Success (200)
   │           │            │           │
   │           │            ├─ API Error
   │           │            │  └─ Retry with backoff
   │           │            │     ├─ Success → Continue
   │           │            │     └─ Fail → 500 Error
   │           │            │
   │           ├─ Channel Not Found
   │           │  └─ 404 Error
   │           │
   └─ Invalid URL
      └─ 400 Error
```

## Scaling Strategy

```
┌────────────────────────────────────────────────────────┐
│              HORIZONTAL SCALING                         │
└────────────────────────────────────────────────────────┘

                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    API Server 1    API Server 2    API Server 3
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Redis Cluster   PostgreSQL      Celery Workers
    (Shared Cache)  (Read Replicas)  (Async Jobs)
```

This architecture ensures:
- ✅ High performance (< 100ms for cached results)
- ✅ Cost efficiency (63% savings with caching)
- ✅ Scalability (horizontal scaling ready)
- ✅ Reliability (proper error handling)
- ✅ Data persistence (database + cache)
