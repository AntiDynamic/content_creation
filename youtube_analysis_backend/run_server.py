"""
Simple server startup script
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("=" * 60)
    print("  YouTube Channel Analyzer - Backend Server")
    print("=" * 60)
    print("\nStarting server...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/v1/docs")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
