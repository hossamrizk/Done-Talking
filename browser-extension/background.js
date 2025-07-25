// background.js - Done-Talking Extension Service Worker

class BackgroundService {
    constructor() {
        this.recordingSessions = new Map();
        this.setupEventListeners();
        console.log('🚀 Done-Talking Extension Background Service Started');
    }
    
    setupEventListeners() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstallation(details);
        });
        
        // Handle messages from content scripts and popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep message channel open for async responses
        });
        
        // Handle tab updates to detect meeting pages
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });
        
        // Handle tab closure to cleanup recording sessions
        chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
            this.handleTabClosed(tabId);
        });
        
        // Handle extension startup
        chrome.runtime.onStartup.addListener(() => {
            console.log('🔄 Done-Talking Extension Service Restarted');
            this.initializeExtension();
        });
    }
    
    handleInstallation(details) {
        console.log('📦 Done-Talking Extension Installed:', details.reason);
        
        if (details.reason === 'install') {
            this.showWelcomeNotification();
            this.setDefaultSettings();
        } else if (details.reason === 'update') {
            console.log('🔄 Extension Updated to version:', chrome.runtime.getManifest().version);
        }
    }
    
    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'recordingStarted':
                    await this.handleRecordingStarted(message, sender);
                    break;
                    
                case 'recordingStopped':
                    await this.handleRecordingStopped(message, sender);
                    break;
                    
                case 'processingComplete':
                    await this.handleProcessingComplete(message, sender);
                    break;
                    
                case 'getRecordingStatus':
                    sendResponse(this.getRecordingStatus(sender.tab.id));
                    break;
                    
                case 'error':
                    this.handleError(message, sender);
                    break;
                    
                default:
                    console.warn('Unknown message action:', message.action);
            }
        } catch (error) {
            console.error('Error handling message:', error);
            sendResponse({ error: error.message });
        }
    }
    
    async handleRecordingStarted(message, sender) {
        const tabId = sender.tab.id;
        const session = {
            tabId: tabId,
            startTime: Date.now(),
            platform: message.platform || 'unknown',
            url: sender.tab.url,
            title: sender.tab.title
        };
        
        this.recordingSessions.set(tabId, session);
        
        // Update badge to show recording status
        await this.updateBadge(tabId, 'recording');
        
        // Log recording session
        console.log(`🎙️ Recording started on ${session.platform}:`, session);
        
        // Store session data
        await this.storeSessionData(session);
    }
    
    async handleRecordingStopped(message, sender) {
        const tabId = sender.tab.id;
        const session = this.recordingSessions.get(tabId);
        
        if (session) {
            session.endTime = Date.now();
            session.duration = session.endTime - session.startTime;
            
            console.log(`⏹️ Recording stopped. Duration: ${this.formatDuration(session.duration)}`);
            
            // Update badge
            await this.updateBadge(tabId, 'processing');
            
            // Update session data
            await this.storeSessionData(session);
        }
    }
    
    async handleProcessingComplete(message, sender) {
        const tabId = sender.tab.id;
        const session = this.recordingSessions.get(tabId);
        
        if (session) {
            session.processed = true;
            session.result = message.result;
            
            console.log('✅ Processing complete for session:', session);
            
            // Clear badge
            await this.updateBadge(tabId, 'complete');
            
            // Clean up session after delay
            setTimeout(() => {
                this.recordingSessions.delete(tabId);
                chrome.action.setBadgeText({ text: '', tabId: tabId });
            }, 5000);
            
            // Update session data
            await this.storeSessionData(session);
            
            // Show success notification
            this.showNotification(
                'Recording Processed',
                'Your meeting has been analyzed by Done-Talking!',
                'success'
            );
        }
    }
    
    handleError(message, sender) {
        const tabId = sender.tab.id;
        console.error('❌ Error from content script:', message.error);
        
        // Clear recording session on error
        this.recordingSessions.delete(tabId);
        
        // Clear badge
        chrome.action.setBadgeText({ text: '', tabId: tabId });
        
        // Show error notification
        this.showNotification(
            'Recording Error',
            message.error || 'An error occurred during recording',
            'error'
        );
    }
    
    handleTabUpdate(tabId, changeInfo, tab) {
        // Detect when user navigates to a meeting platform
        if (changeInfo.status === 'complete' && tab.url) {
            const platform = this.detectPlatform(tab.url);
            if (platform !== 'unknown') {
                console.log(`📍 Meeting platform detected: ${platform} on tab ${tabId}`);
                // Could show a subtle notification or update icon
            }
        }
    }
    
    handleTabClosed(tabId) {
        // Clean up any active recording sessions
        if (this.recordingSessions.has(tabId)) {
            console.log(`🗑️ Cleaning up recording session for closed tab ${tabId}`);
            this.recordingSessions.delete(tabId);
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
    
    async updateBadge(tabId, status) {
        const badges = {
            'recording': { text: '●', color: '#ff0000' },
            'processing': { text: '⏳', color: '#ff9800' },
            'complete': { text: '✓', color: '#4caf50' }
        };
        
        const badge = badges[status];
        if (badge) {
            await chrome.action.setBadgeText({ text: badge.text, tabId: tabId });
            await chrome.action.setBadgeBackgroundColor({ color: badge.color, tabId: tabId });
        }
    }
    
    getRecordingStatus(tabId) {
        const session = this.recordingSessions.get(tabId);
        return session ? {
            isRecording: !session.endTime,
            startTime: session.startTime,
            platform: session.platform,
            duration: session.endTime ? session.duration : Date.now() - session.startTime
        } : { isRecording: false };
    }
    
    async storeSessionData(session) {
        try {
            const sessionId = `session_${session.tabId}_${session.startTime}`;
            await chrome.storage.local.set({ [sessionId]: session });
        } catch (error) {
            console.error('Error storing session data:', error);
        }
    }
    
    async setDefaultSettings() {
        const defaultSettings = {
            apiEndpoint: 'http://localhost:8000',
            autoDownload: true,
            showNotifications: true,
            audioQuality: 'high',
            version: chrome.runtime.getManifest().version
        };
        
        await chrome.storage.sync.set({ settings: defaultSettings });
        console.log('⚙️ Default settings applied:', defaultSettings);
    }
    
    showWelcomeNotification() {
        this.showNotification(
            'Done-Talking Installed!',
            'Extension ready. Join a meeting and click the record button to start.',
            'info'
        );
    }
    
    showNotification(title, message, type = 'info') {
        // Check if notifications are enabled
        chrome.storage.sync.get(['settings'], (result) => {
            if (result.settings && result.settings.showNotifications !== false) {
                const iconMap = {
                    'success': '✅',
                    'error': '❌',
                    'info': 'ℹ️',
                    'warning': '⚠️'
                };
                
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon48.png',
                    title: `${iconMap[type] || ''} ${title}`,
                    message: message
                });
            }
        });
    }
    
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    initializeExtension() {
        // Perform any initialization tasks
        console.log('🔧 Initializing Done-Talking Extension...');
        
        // Clear any stale badges
        chrome.tabs.query({}, (tabs) => {
            tabs.forEach(tab => {
                chrome.action.setBadgeText({ text: '', tabId: tab.id });
            });
        });
    }
    
    // Utility method to get all stored sessions
    async getAllSessions() {
        return new Promise((resolve) => {
            chrome.storage.local.get(null, (result) => {
                const sessions = Object.keys(result)
                    .filter(key => key.startsWith('session_'))
                    .map(key => result[key]);
                resolve(sessions);
            });
        });
    }
    
    // Utility method to clear old sessions (call periodically)
    async cleanupOldSessions() {
        const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        
        chrome.storage.local.get(null, (result) => {
            Object.keys(result).forEach(key => {
                if (key.startsWith('session_')) {
                    const session = result[key];
                    if (session.startTime < oneWeekAgo) {
                        chrome.storage.local.remove(key);
                    }
                }
            });
        });
    }
}

// Initialize the background service
const backgroundService = new BackgroundService();

// Cleanup old sessions once per day
setInterval(() => {
    backgroundService.cleanupOldSessions();
}, 24 * 60 * 60 * 1000);