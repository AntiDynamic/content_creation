# YouTube Channel Analysis Platform

A comprehensive YouTube channel analysis platform with AI-powered insights using Google's Gemini API.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/AntiDynamic/content_creation)

## 🚀 Live Demo

- **Production**: https://contentcreation-six.vercel.app
- **API Docs**: https://contentcreation-six.vercel.app/docs

## 📁 Project Structure

```
content_creation/
├── backend/              # FastAPI backend service
│   ├── main.py          # Main FastAPI application
│   ├── analysis_service.py
│   ├── gemini_service.py
│   ├── youtube_service.py
│   ├── models.py        # Pydantic models
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── cache.py         # Caching utilities
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables template
│
├── frontend/            # Web interface
│   ├── index.html      # Main HTML page
│   ├── script.js       # JavaScript functionality
│   ├── style.css       # Styling
│   └── README.md       # Frontend documentation
│
├── docs/               # Documentation
│   ├── README.md       # Main project documentation
│   ├── ARCHITECTURE.md # System architecture
│   ├── QUICKSTART.md   # Quick start guide
│   ├── QUICKSTART_TESTING.md
│   ├── PROJECT_SUMMARY.md
│   ├── IMPLEMENTATION_VERIFICATION.md
│   ├── RUNNING_STATUS.md
│   ├── VISUAL_OVERVIEW.md
│   ├── youtube_v3_documentation.md
│   └── youtube_channel_analysis_workflow.md
│
├── scripts/            # Utility scripts
│   ├── RUN_ME.bat     # Main launcher
│   ├── start.bat      # Start script
│   ├── start_server.bat
│   ├── setup.ps1      # PowerShell setup
│   └── setup.sh       # Bash setup
│
├── tests/             # Test files
│   ├── test_api.py
│   ├── test_backend.py
│   ├── test_analysis.py
│   └── test_direct.py
│
└── .gitignore         # Git ignore rules
```

## 🚀 Quick Start

### Local Development

1. **Setup Environment**
   ```bash
   # Clone the repository
   git clone https://github.com/AntiDynamic/content_creation.git
   cd content_creation
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r backend/requirements.txt
   ```

2. **Configure API Keys**
   - Copy `backend\.env.example` to `backend\.env`
   - Add your API keys (YouTube Data API, Gemini API)

3. **Run the Application**
   ```bash
   # Windows
   .\scripts\RUN_ME.bat
   
   # Linux/Mac
   cd backend
   python main.py
   ```

4. **Access the Application**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Link and deploy
vercel link
vercel --prod
```

Don't forget to add your environment variables in Vercel dashboard:
- `YOUTUBE_API_KEY`
- `GEMINI_API_KEY`

## 📚 Documentation

For detailed documentation, see the [docs](./docs/) directory:
- [Architecture](./docs/ARCHITECTURE.md) - System design and architecture
- [Quick Start](./docs/QUICKSTART.md) - Getting started guide
- [API Documentation](./docs/README.md) - API reference

## 🧪 Testing

Run tests from the project root:
```bash
cd backend
python -m pytest ../tests/
```

## 📄 License

See individual files for licensing information.
