# YouTube Channel Analyzer - Frontend

A beautiful, modern web interface for analyzing YouTube channels using AI-powered insights.

## 🎨 Features

- **Stunning UI**: Modern glassmorphism design with smooth animations
- **Simple Input**: Just paste a YouTube channel URL
- **Real-time Analysis**: Get AI-powered insights in seconds
- **Comprehensive Results**: View channel summary, themes, audience, content style, and more
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites

Make sure the backend server is running:

```bash
# From the youtube_analysis_backend directory
python main.py
```

The backend should be running at `http://localhost:8000`

### Running the Frontend

Simply open `index.html` in your web browser:

1. **Double-click** `index.html`, or
2. **Right-click** → Open with → Your preferred browser, or
3. Use a local server (recommended for development):

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve

# Using VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

Then navigate to:
- `http://localhost:8080` (if using Python)
- `http://localhost:3000` (if using npx serve)
- Auto-opens if using VS Code Live Server

## 📝 How to Use

1. **Enter a YouTube Channel URL**
   - Supported formats:
     - `https://youtube.com/@username`
     - `https://youtube.com/channel/UC...`
     - `https://youtube.com/c/channelname`
     - `https://youtube.com/user/username`

2. **Click "Analyze Channel"**
   - First-time analysis: 10-30 seconds
   - Cached results: < 100ms

3. **View Results**
   - Channel information (subscribers, videos)
   - AI-generated summary
   - Content themes
   - Target audience analysis
   - Content style description
   - Upload frequency

## 🎯 Example Channels to Try

- `https://youtube.com/@mkbhd` - Tech reviews
- `https://youtube.com/@veritasium` - Science education
- `https://youtube.com/@3blue1brown` - Math visualization

## 🛠️ Technology Stack

- **HTML5**: Semantic structure with SEO optimization
- **CSS3**: Modern design with CSS variables, animations, and glassmorphism
- **Vanilla JavaScript**: No frameworks, pure performance
- **Google Fonts**: Inter font family for premium typography

## 📱 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## 🎨 Design Features

- **Glassmorphism**: Frosted glass effect with backdrop blur
- **Gradient Orbs**: Animated background effects
- **Smooth Animations**: CSS transitions and keyframes
- **Responsive Layout**: Mobile-first design approach
- **Dark Theme**: Easy on the eyes with vibrant accents
- **Micro-interactions**: Hover effects and button animations

## 🔧 Configuration

The frontend connects to the backend API at `http://localhost:8000` by default.

To change the API URL, edit `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
const API_VERSION = 'v1';
```

## 📊 API Integration

The frontend communicates with the backend using:

- **POST** `/v1/analyze` - Analyze a channel
- **GET** `/health` - Check API status
- **GET** `/` - API information

## 🐛 Troubleshooting

### "API Offline" status badge

**Solution**: Make sure the backend server is running:
```bash
python main.py
```

### CORS errors

**Solution**: The backend is configured to allow all origins. If you still see CORS errors, check that the backend is running on `http://localhost:8000`

### Analysis takes too long

**Possible causes**:
- First-time analysis of a large channel
- Slow internet connection
- API rate limits

**Solution**: Wait for the analysis to complete. Subsequent analyses will be much faster due to caching.

## 📄 Files

- `index.html` - Main HTML structure
- `style.css` - All styling and animations
- `script.js` - API integration and UI logic

## 🎯 Future Enhancements

- [ ] Channel comparison feature
- [ ] Export results as PDF
- [ ] Historical analysis tracking
- [ ] Video-level insights
- [ ] Competitor analysis

## 📝 License

Part of the YouTube Channel Analyzer project.

---

**Powered by Google Gemini AI & YouTube Data API v3**
