# Backend - YouTube Analysis API

FastAPI-based backend service for YouTube channel analysis.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Server**
   ```bash
   python main.py
   ```

## API Endpoints

- `GET /` - Serves the frontend
- `POST /api/analyze` - Analyze YouTube channel
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation

## Environment Variables

See `.env.example` for required configuration.

## Core Modules

- `main.py` - FastAPI application and routes
- `analysis_service.py` - Channel analysis logic
- `gemini_service.py` - Gemini API integration
- `youtube_service.py` - YouTube Data API integration
- `models.py` - Data models
- `config.py` - Configuration management
- `database.py` - Database setup
- `cache.py` - Caching utilities
