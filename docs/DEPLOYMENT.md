# Deployment Guide

## Vercel Deployment

### Prerequisites
- Vercel CLI installed (`npm i -g vercel`)
- GitHub repository connected
- API keys ready (YouTube Data API, Gemini API)

### Steps

1. **Link Project to Vercel**
   ```bash
   vercel link --yes
   ```

2. **Add Environment Variables**
   
   Go to your Vercel dashboard and add these environment variables:
   - `YOUTUBE_API_KEY` - Your YouTube Data API key
   - `GEMINI_API_KEY` - Your Google Gemini API key

   Or add them via CLI:
   ```bash
   vercel env add YOUTUBE_API_KEY
   vercel env add GEMINI_API_KEY
   ```

3. **Deploy to Production**
   ```bash
   vercel --prod
   ```

### Deployment URLs

- **Production**: https://contentcreation-six.vercel.app
- **API Documentation**: https://contentcreation-six.vercel.app/docs
- **Preview**: Automatic deployment on every push to main branch

## Alternative: Netlify Deployment

### Using Netlify CLI

1. **Install Netlify CLI**
   ```bash
   npm i -g netlify-cli
   ```

2. **Login and Deploy**
   ```bash
   netlify login
   netlify init
   netlify deploy --prod
   ```

3. **Add Environment Variables**
   
   In Netlify dashboard, add:
   - `YOUTUBE_API_KEY`
   - `GEMINI_API_KEY`

## GitHub Pages (Frontend Only)

For static frontend deployment:

```bash
# Build frontend
# (No build step required - pure HTML/CSS/JS)

# Deploy to GitHub Pages
git checkout -b gh-pages
git push origin gh-pages
```

Then enable GitHub Pages in repository settings.

## Environment Variables

Required environment variables for all deployments:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional:
```
PORT=8000
LOG_LEVEL=info
```

## Continuous Deployment

### Vercel
- Auto-deploys on push to `main` branch
- Preview deployments for pull requests

### Netlify
- Auto-deploys on push to configured branch
- Deploy previews for pull requests

## Troubleshooting

### Build Failures
- Ensure all dependencies are in `backend/requirements.txt`
- Check Python version compatibility (3.11+)

### Environment Variables Not Loading
- Verify variables are set in deployment platform dashboard
- Restart deployment after adding variables

### API Connection Issues
- Verify API keys are valid
- Check API quotas and limits
- Review CORS settings if needed
