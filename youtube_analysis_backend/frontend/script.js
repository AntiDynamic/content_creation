/**
 * YouTube Channel Analyzer - Frontend JavaScript
 * Handles API communication and UI state management
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_VERSION = 'v1';

// DOM Elements
const elements = {
    form: document.getElementById('analyzeForm'),
    channelUrlInput: document.getElementById('channelUrl'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loadingState: document.getElementById('loadingState'),
    resultsSection: document.getElementById('resultsSection'),
    errorState: document.getElementById('errorState'),
    statusBadge: document.getElementById('statusBadge'),

    // Results elements
    channelThumbnail: document.getElementById('channelThumbnail'),
    channelTitle: document.getElementById('channelTitle'),
    subscriberCount: document.getElementById('subscriberCount'),
    videoCount: document.getElementById('videoCount'),
    videosAnalyzed: document.getElementById('videosAnalyzed'),
    summaryText: document.getElementById('summaryText'),
    themesList: document.getElementById('themesList'),
    audienceText: document.getElementById('audienceText'),
    styleText: document.getElementById('styleText'),
    frequencyText: document.getElementById('frequencyText'),
    confidence: document.getElementById('confidence'),
    freshness: document.getElementById('freshness'),
    source: document.getElementById('source'),
    analyzedAt: document.getElementById('analyzedAt'),

    // Error elements
    errorTitle: document.getElementById('errorTitle'),
    errorMessage: document.getElementById('errorMessage'),

    // Buttons
    analyzeAnotherBtn: document.getElementById('analyzeAnotherBtn'),
    tryAgainBtn: document.getElementById('tryAgainBtn')
};

// State
let currentStep = 1;
let stepInterval = null;

/**
 * Initialize the application
 */
function init() {
    // Check API health
    checkAPIHealth();

    // Event listeners
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.analyzeAnotherBtn.addEventListener('click', resetForm);
    elements.tryAgainBtn.addEventListener('click', resetForm);

    // Auto-focus input
    elements.channelUrlInput.focus();
}

/**
 * Check if the API is running
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatusBadge('online');
        } else {
            updateStatusBadge('offline');
        }
    } catch (error) {
        updateStatusBadge('offline');
    }
}

/**
 * Update status badge
 */
function updateStatusBadge(status) {
    const badge = elements.statusBadge;
    const dot = badge.querySelector('.status-dot');
    const text = badge.querySelector('span:last-child');

    if (status === 'online') {
        badge.style.background = 'rgba(16, 185, 129, 0.1)';
        badge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        badge.style.color = '#10B981';
        dot.style.background = '#10B981';
        text.textContent = 'API Ready';
    } else {
        badge.style.background = 'rgba(239, 68, 68, 0.1)';
        badge.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        badge.style.color = '#EF4444';
        dot.style.background = '#EF4444';
        text.textContent = 'API Offline';
    }
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    const channelUrl = elements.channelUrlInput.value.trim();

    if (!channelUrl) {
        showError('Invalid Input', 'Please enter a valid YouTube channel URL');
        return;
    }

    // Validate URL format
    if (!isValidYouTubeUrl(channelUrl)) {
        showError('Invalid URL', 'Please enter a valid YouTube channel URL (e.g., https://youtube.com/@username)');
        return;
    }

    // Start analysis
    await analyzeChannel(channelUrl);
}

/**
 * Validate YouTube URL
 */
function isValidYouTubeUrl(url) {
    const patterns = [
        /youtube\.com\/@[\w-]+/,
        /youtube\.com\/channel\/[\w-]+/,
        /youtube\.com\/c\/[\w-]+/,
        /youtube\.com\/user\/[\w-]+/
    ];

    return patterns.some(pattern => pattern.test(url));
}

/**
 * Analyze channel
 */
async function analyzeChannel(channelUrl) {
    // Show loading state
    showLoading();

    // Start step animation
    startStepAnimation();

    try {
        const response = await fetch(`${API_BASE_URL}/${API_VERSION}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ channel_url: channelUrl })
        });

        const data = await response.json();

        // Stop step animation
        stopStepAnimation();

        if (response.ok) {
            // Show results
            displayResults(data);
        } else {
            // Show error
            const errorData = data.detail || data;
            showError(
                errorData.error || 'Analysis Failed',
                errorData.details || errorData.error_code || 'An error occurred while analyzing the channel'
            );
        }
    } catch (error) {
        stopStepAnimation();
        console.error('Analysis error:', error);
        showError(
            'Connection Error',
            'Unable to connect to the API. Please make sure the backend server is running on http://localhost:8000'
        );
    }
}

/**
 * Show loading state
 */
function showLoading() {
    elements.loadingState.classList.add('active');
    elements.resultsSection.classList.remove('active');
    elements.errorState.classList.remove('active');
    elements.analyzeBtn.disabled = true;
}

/**
 * Hide loading state
 */
function hideLoading() {
    elements.loadingState.classList.remove('active');
    elements.analyzeBtn.disabled = false;
}

/**
 * Start step animation
 */
function startStepAnimation() {
    currentStep = 1;
    updateStepUI();

    stepInterval = setInterval(() => {
        currentStep = (currentStep % 3) + 1;
        updateStepUI();
    }, 3000);
}

/**
 * Stop step animation
 */
function stopStepAnimation() {
    if (stepInterval) {
        clearInterval(stepInterval);
        stepInterval = null;
    }
}

/**
 * Update step UI
 */
function updateStepUI() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index + 1 <= currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

/**
 * Display results
 */
function displayResults(data) {
    hideLoading();

    const { channel, analysis, meta } = data;

    // Channel info
    elements.channelThumbnail.src = channel.thumbnail_url || 'https://via.placeholder.com/120';
    elements.channelThumbnail.alt = channel.title;
    elements.channelTitle.textContent = channel.title;
    elements.subscriberCount.textContent = formatNumber(channel.subscriber_count);
    elements.videoCount.textContent = formatNumber(channel.video_count);
    elements.videosAnalyzed.textContent = meta.videos_analyzed;

    // Analysis
    elements.summaryText.textContent = analysis.summary;

    // Themes
    elements.themesList.innerHTML = '';
    analysis.themes.forEach(theme => {
        const tag = document.createElement('div');
        tag.className = 'theme-tag';
        tag.textContent = theme;
        elements.themesList.appendChild(tag);
    });

    elements.audienceText.textContent = analysis.target_audience;
    elements.styleText.textContent = analysis.content_style;
    elements.frequencyText.textContent = analysis.upload_frequency;

    // Metadata
    elements.confidence.textContent = `${(meta.confidence * 100).toFixed(0)}%`;
    elements.freshness.textContent = meta.freshness;
    elements.source.textContent = meta.source || 'API';
    elements.analyzedAt.textContent = formatDate(meta.analyzed_at);

    // Show results
    elements.resultsSection.classList.add('active');

    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Show error
 */
function showError(title, message) {
    hideLoading();

    elements.errorTitle.textContent = title;
    elements.errorMessage.textContent = message;
    elements.errorState.classList.add('active');

    // Scroll to error
    setTimeout(() => {
        elements.errorState.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

/**
 * Reset form
 */
function resetForm() {
    elements.form.reset();
    elements.resultsSection.classList.remove('active');
    elements.errorState.classList.remove('active');
    elements.channelUrlInput.focus();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

/**
 * Add example URLs for quick testing (optional)
 */
function addExampleUrls() {
    const examples = [
        'https://youtube.com/@mkbhd',
        'https://youtube.com/@veritasium',
        'https://youtube.com/@3blue1brown'
    ];

    // You can add a UI element to show these examples if needed
    console.log('Example URLs:', examples);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isValidYouTubeUrl,
        formatNumber,
        formatDate
    };
}
