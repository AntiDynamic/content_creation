/**
 * YouTube Channel Analyzer - Strategic Analysis Frontend
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

    // Profile elements
    profileSection: document.getElementById('profileSection'),
    profileThumbnail: document.getElementById('profileThumbnail'),
    profileName: document.getElementById('profileName'),
    profileSubs: document.getElementById('profileSubs'),
    profileVideos: document.getElementById('profileVideos'),
    changeChannelBtn: document.getElementById('changeChannelBtn'),
    reanalyzeBtn: document.getElementById('reanalyzeBtn'),
    heroSection: document.getElementById('heroSection'),
    inputSection: document.querySelector('.input-section'),

    // Channel info
    channelThumbnail: document.getElementById('channelThumbnail'),
    channelTitle: document.getElementById('channelTitle'),
    subscriberCount: document.getElementById('subscriberCount'),
    videoCount: document.getElementById('videoCount'),
    videosAnalyzed: document.getElementById('videosAnalyzed'),

    // Scores
    overallScore: document.getElementById('overallScore'),
    consistencyScore: document.getElementById('consistencyScore'),
    engagementScore: document.getElementById('engagementScore'),
    growthScore: document.getElementById('growthScore'),

    // Analysis content
    verdictText: document.getElementById('verdictText'),
    strengthsList: document.getElementById('strengthsList'),
    weaknessesList: document.getElementById('weaknessesList'),
    strategiesList: document.getElementById('strategiesList'),
    recommendationsList: document.getElementById('recommendationsList'),
    thumbnailAdvice: document.getElementById('thumbnailAdvice'),
    titleAdvice: document.getElementById('titleAdvice'),
    uploadSchedule: document.getElementById('uploadSchedule'),
    engagementTips: document.getElementById('engagementTips'),

    // Videos
    topVideosList: document.getElementById('topVideosList'),
    recentVideosList: document.getElementById('recentVideosList'),

    // Metadata
    modelVersion: document.getElementById('modelVersion'),
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
let savedProfile = null;

/**
 * Initialize the application
 */
function init() {
    // Load saved profile from localStorage
    loadSavedProfile();

    // Check API health
    checkAPIHealth();

    // Event listeners
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.analyzeAnotherBtn.addEventListener('click', resetForm);
    elements.tryAgainBtn.addEventListener('click', resetForm);
    
    // Profile event listeners
    if (elements.changeChannelBtn) {
        elements.changeChannelBtn.addEventListener('click', handleChangeChannel);
    }
    if (elements.reanalyzeBtn) {
        elements.reanalyzeBtn.addEventListener('click', handleReanalyze);
    }

    // Tab switching for videos
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabClick);
    });

    // Auto-focus input if no saved profile
    if (!savedProfile) {
        elements.channelUrlInput.focus();
    }
}

/**
 * Load saved profile from localStorage
 */
function loadSavedProfile() {
    const saved = localStorage.getItem('youtubeAnalyzerProfile');
    if (saved) {
        try {
            savedProfile = JSON.parse(saved);
            showProfile(savedProfile);
        } catch (e) {
            localStorage.removeItem('youtubeAnalyzerProfile');
        }
    }
}

/**
 * Save profile to localStorage
 */
function saveProfile(channelData) {
    const profile = {
        channelUrl: channelData.channelUrl || elements.channelUrlInput.value.trim(),
        title: channelData.title,
        thumbnail: channelData.thumbnail_url,
        subscribers: channelData.subscriber_count,
        videos: channelData.video_count
    };
    localStorage.setItem('youtubeAnalyzerProfile', JSON.stringify(profile));
    savedProfile = profile;
}

/**
 * Show the profile section
 */
function showProfile(profile) {
    if (!profile) return;
    
    elements.profileThumbnail.src = profile.thumbnail;
    elements.profileName.textContent = profile.title;
    elements.profileSubs.textContent = formatNumber(profile.subscribers);
    elements.profileVideos.textContent = formatNumber(profile.videos);
    
    elements.profileSection.style.display = 'block';
    elements.heroSection.style.display = 'none';
    elements.inputSection.style.display = 'none';
}

/**
 * Hide profile and show input form
 */
function hideProfile() {
    elements.profileSection.style.display = 'none';
    elements.heroSection.style.display = 'block';
    elements.inputSection.style.display = 'block';
}

/**
 * Handle change channel button click
 */
function handleChangeChannel() {
    localStorage.removeItem('youtubeAnalyzerProfile');
    savedProfile = null;
    hideProfile();
    resetForm();
    elements.channelUrlInput.value = '';
    elements.channelUrlInput.focus();
}

/**
 * Handle reanalyze button click
 */
function handleReanalyze() {
    if (savedProfile && savedProfile.channelUrl) {
        elements.channelUrlInput.value = savedProfile.channelUrl;
        analyzeChannel(savedProfile.channelUrl);
    }
}

/**
 * Handle tab click for video lists
 */
function handleTabClick(event) {
    const tab = event.target.dataset.tab;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Show correct video list
    if (tab === 'top') {
        elements.topVideosList.classList.remove('hidden');
        elements.recentVideosList.classList.add('hidden');
    } else {
        elements.topVideosList.classList.add('hidden');
        elements.recentVideosList.classList.remove('hidden');
    }
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
 * Analyze channel using strategic endpoint
 */
async function analyzeChannel(channelUrl) {
    // Show loading state
    showLoading();

    // Start step animation
    startStepAnimation();

    try {
        const response = await fetch(`${API_BASE_URL}/${API_VERSION}/analyze/strategic`, {
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
            displayStrategicResults(data);
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
    }, 5000);
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
 * Display strategic analysis results
 */
function displayStrategicResults(data) {
    hideLoading();

    const { channel, analysis, meta, top_videos, recent_videos } = data;

    // Save profile for future use
    saveProfile({
        channelUrl: elements.channelUrlInput.value.trim(),
        title: channel.title,
        thumbnail_url: channel.thumbnail_url,
        subscriber_count: channel.subscriber_count,
        video_count: channel.video_count
    });
    showProfile(savedProfile);

    // Channel info
    elements.channelThumbnail.src = channel.thumbnail_url || 'https://via.placeholder.com/120';
    elements.channelThumbnail.alt = channel.title;
    elements.channelTitle.textContent = channel.title;
    elements.subscriberCount.textContent = formatNumber(channel.subscriber_count);
    elements.videoCount.textContent = formatNumber(channel.video_count);
    elements.videosAnalyzed.textContent = meta.videos_analyzed;

    // Scores with animation
    animateScore(elements.overallScore, analysis.scores?.overall || 0);
    animateScore(elements.consistencyScore, analysis.scores?.consistency || 0);
    animateScore(elements.engagementScore, analysis.scores?.engagement || 0);
    animateScore(elements.growthScore, analysis.scores?.growth_potential || 0);

    // Overall verdict
    elements.verdictText.textContent = analysis.overall_verdict || 'Analysis complete.';

    // Strengths
    elements.strengthsList.innerHTML = '';
    (analysis.strengths || []).forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        elements.strengthsList.appendChild(li);
    });

    // Weaknesses
    elements.weaknessesList.innerHTML = '';
    (analysis.weaknesses || []).forEach(weakness => {
        const li = document.createElement('li');
        li.textContent = weakness;
        elements.weaknessesList.appendChild(li);
    });

    // Growth strategies
    elements.strategiesList.innerHTML = '';
    (analysis.growth_strategy || []).forEach(strategy => {
        const card = document.createElement('div');
        card.className = 'strategy-card';
        card.innerHTML = `
            <div class="strategy-priority ${getPriorityClass(strategy.priority)}">${strategy.priority}</div>
            <h4 class="strategy-action">${strategy.action}</h4>
            <div class="strategy-meta">
                <span class="strategy-impact">📈 ${strategy.expected_impact}</span>
                <span class="strategy-timeline">⏱️ ${strategy.timeline}</span>
            </div>
        `;
        elements.strategiesList.appendChild(card);
    });

    // Content recommendations
    elements.recommendationsList.innerHTML = '';
    (analysis.content_recommendations || []).forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.innerHTML = `
            <div class="rec-type">${rec.type}</div>
            <p class="rec-description">${rec.description}</p>
            <div class="rec-frequency">📅 ${rec.frequency}</div>
            <div class="rec-topics">
                <strong>Example topics:</strong>
                <ul>
                    ${(rec.example_topics || []).map(topic => `<li>${topic}</li>`).join('')}
                </ul>
            </div>
        `;
        elements.recommendationsList.appendChild(card);
    });

    // Quick tips
    elements.thumbnailAdvice.textContent = analysis.thumbnail_advice || 'No specific advice.';
    elements.titleAdvice.textContent = analysis.title_advice || 'No specific advice.';
    elements.uploadSchedule.textContent = analysis.upload_schedule || 'No specific schedule.';

    // Engagement tips
    elements.engagementTips.innerHTML = '';
    (analysis.engagement_tips || []).forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        elements.engagementTips.appendChild(li);
    });

    // Top videos
    elements.topVideosList.innerHTML = '';
    (top_videos || []).forEach(video => {
        elements.topVideosList.appendChild(createVideoCard(video));
    });

    // Recent videos
    elements.recentVideosList.innerHTML = '';
    (recent_videos || []).forEach(video => {
        elements.recentVideosList.appendChild(createVideoCard(video));
    });

    // Metadata
    elements.modelVersion.textContent = meta.model_version || 'Gemini';
    elements.analyzedAt.textContent = formatDate(meta.analyzed_at);

    // Show results
    elements.resultsSection.classList.add('active');

    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Create video card element
 */
function createVideoCard(video) {
    const card = document.createElement('div');
    card.className = 'video-card';
    card.innerHTML = `
        <div class="video-thumbnail">
            <img src="${video.thumbnail_url || 'https://via.placeholder.com/320x180'}" alt="${video.title}">
        </div>
        <div class="video-info">
            <h4 class="video-title">${video.title}</h4>
            <div class="video-stats">
                <span>👁️ ${formatNumber(video.views)}</span>
                <span>👍 ${formatNumber(video.likes)}</span>
                <span>💬 ${formatNumber(video.comments)}</span>
            </div>
            <div class="video-date">${formatDate(video.published_at)}</div>
        </div>
    `;
    return card;
}

/**
 * Animate score display
 */
function animateScore(element, targetScore) {
    const scoreValue = element.querySelector('.score-value');
    let current = 0;
    const duration = 1000;
    const steps = 30;
    const increment = targetScore / steps;
    const stepDuration = duration / steps;

    // Set color based on score
    element.style.setProperty('--score-color', getScoreColor(targetScore));

    const timer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
            current = targetScore;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(current);
    }, stepDuration);
}

/**
 * Get score color based on value
 */
function getScoreColor(score) {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#8B5CF6';
    if (score >= 40) return '#F59E0B';
    return '#EF4444';
}

/**
 * Get priority class for strategies
 */
function getPriorityClass(priority) {
    if (!priority) return 'medium';
    const p = priority.toLowerCase();
    if (p.includes('high') || p.includes('critical')) return 'high';
    if (p.includes('low')) return 'low';
    return 'medium';
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

    // Reset tabs
    document.querySelectorAll('.tab-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === 0);
    });
    elements.topVideosList.classList.remove('hidden');
    elements.recentVideosList.classList.add('hidden');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    if (!num) return '0';
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
    if (!dateString) return 'Unknown';
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
