// popup.js - Done-Talking Extension Popup Logic

class PopupController {
    constructor() {
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        this.currentTab = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.checkCurrentState();
    }
    
    initializeElements() {
        this.elements = {
            statusCard: document.getElementById('statusCard'),
            statusIcon: document.getElementById('statusIcon'),
            statusText: document.getElementById('statusText'),
            statusSubtext: document.getElementById('statusSubtext'),
            platformIndicator: document.getElementById('platformIndicator'),
            recordBtn: document.getElementById('recordBtn'),
            settingsBtn: document.getElementById('settingsBtn'),
            errorMessage: document.getElementById('errorMessage'),
            successMessage: document.getElementById('successMessage'),
            stats: document.getElementById('stats'),
            recordingTime: document.getElementById('recordingTime'),
            fileSize: document.getElementById('fileSize')
        };
    }
    
    setupEventListeners() {
        this.elements.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.elements.settingsBtn.addEventListener('click', () => this.openSettings());
        
        // Listen for messages from content script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message);
        });
    }
    
    async checkCurrentState() {
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tab;
            
            // Check if we're on a supported meeting platform
            const platform = this.detectPlatform(tab.url);
            if (platform !== 'unknown') {
                this.updatePlatformIndicator(platform);
            }
            
            // Check recording status from content script
            chrome.tabs.sendMessage(tab.id, { action: 'getStatus' }, (response) => {
                if (chrome.runtime.lastError) {
                    this.updateStatus('not-supported', 'Extension Not Active', 'This page doesn\'t support recording');
                    return;
                }
                
                if (response) {
                    this.updateRecordingState(response);
                }
            });
            
        } catch (error) {
            console.error('Error checking current state:', error);
            this.showError('Failed to check recording status');
        }
    }
    
    detectPlatform(url) {
        if (!url) return 'unknown';
        
        if (url.includes('meet.google.com')) return 'google-meet';
        if (url.includes('zoom.us')) return 'zoom';
        if (url.includes('teams.microsoft.com')) return 'teams';
        if (url.includes('webex.com')) return 'webex';
        return 'unknown';
    }
    
    updatePlatformIndicator(platform) {
        const platformNames = {
            'google-meet': '📹 Google Meet',
            'zoom': '🔵 Zoom',
            'teams': '💼 Teams',
            'webex': '🌐 WebEx'
        };
        
        this.elements.platformIndicator.textContent = platformNames[platform] || platform;
        this.elements.platformIndicator.style.display = 'inline-block';
    }
    
    async toggleRecording() {
        if (!this.currentTab) {
            this.showError('No active tab found');
            return;
        }
        
        try {
            // Send toggle command to content script
            chrome.tabs.sendMessage(this.currentTab.id, { action: 'toggleRecording' }, (response) => {
                if (chrome.runtime.lastError) {
                    this.showError('Failed to communicate with recording script');
                    return;
                }
                
                if (response && response.error) {
                    this.showError(response.error);
                }
            });
            
        } catch (error) {
            console.error('Error toggling recording:', error);
            this.showError('Failed to toggle recording');
        }
    }
    
    updateRecordingState(state) {
        this.isRecording = state.isRecording;
        
        if (state.isRecording) {
            this.startRecordingUI();
            if (state.startTime) {
                this.recordingStartTime = new Date(state.startTime);
                this.startTimer();
            }
        } else {
            this.stopRecordingUI();
            this.stopTimer();
        }
        
        if (state.platform) {
            this.updatePlatformIndicator(state.platform);
        }
    }
    
    startRecordingUI() {
        this.updateStatus('recording', '🔴 Recording', 'Meeting audio is being captured');
        this.elements.recordBtn.textContent = '⏹️ Stop Recording';
        this.elements.recordBtn.className = 'button danger';
        this.elements.stats.style.display = 'block';
        this.startTimer();
    }
    
    stopRecordingUI() {
        this.updateStatus('ready', '✅ Ready', 'Ready to start recording');
        this.elements.recordBtn.textContent = '🎙️ Start Recording';
        this.elements.recordBtn.className = 'button primary';
        this.elements.stats.style.display = 'none';
        this.stopTimer();
    }
    
    updateStatus(type, text, subtext) {
        // Update status card appearance
        this.elements.statusCard.className = `status-card ${type}`;
        
        // Update status content
        this.elements.statusText.textContent = text;
        this.elements.statusSubtext.textContent = subtext;
        
        // Update status icon
        const icons = {
            'ready': '✅',
            'recording': '🔴',
            'processing': '⏳',
            'not-supported': '❌'
        };
        this.elements.statusIcon.textContent = icons[type] || '❓';
    }
    
    startTimer() {
        if (this.recordingTimer) return;
        
        this.recordingTimer = setInterval(() => {
            if (this.recordingStartTime) {
                const elapsed = Date.now() - this.recordingStartTime.getTime();
                this.elements.recordingTime.textContent = this.formatTime(elapsed);
                
                // Estimate file size (rough calculation)
                const estimatedSize = Math.floor(elapsed / 1000) * 16; // ~16KB per second
                this.elements.fileSize.textContent = this.formatFileSize(estimatedSize * 1024);
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }
    
    formatTime(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    handleMessage(message) {
        switch (message.action) {
            case 'recordingStarted':
                this.recordingStartTime = new Date();
                this.startRecordingUI();
                this.showSuccess('Recording started successfully!');
                break;
                
            case 'recordingStopped':
                this.stopRecordingUI();
                this.showSuccess('Recording stopped and processing...');
                break;
                
            case 'processingComplete':
                this.showSuccess('Meeting processed successfully!');
                break;
                
            case 'error':
                this.showError(message.message || 'An error occurred');
                this.stopRecordingUI();
                break;
                
            case 'statusUpdate':
                this.updateRecordingState(message.status);
                break;
        }
    }
    
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorMessage.style.display = 'block';
        this.elements.successMessage.style.display = 'none';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.elements.errorMessage.style.display = 'none';
        }, 5000);
    }
    
    showSuccess(message) {
        this.elements.successMessage.textContent = message;
        this.elements.successMessage.style.display = 'block';
        this.elements.errorMessage.style.display = 'none';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            this.elements.successMessage.style.display = 'none';
        }, 3000);
    }
    
    openSettings() {
        // TODO: Implement settings page
        chrome.tabs.create({
            url: chrome.runtime.getURL('options.html')
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupController();
});

// Handle popup being closed and reopened
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Popup became visible, refresh state
        setTimeout(() => {
            const controller = new PopupController();
        }, 100);
    }
});