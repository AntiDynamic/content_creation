import sys
sys.path.append('.')

from backend.main import app

# Vercel serverless function handler
handler = app

