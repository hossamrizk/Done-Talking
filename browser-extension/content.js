// Enhanced Debug Version - Shows real-time audio status
class DoneTalkingRecorder {
    constructor() {
        this.isRecording = false;
        this.recorder = null;
        this.audioChunks = [];
        this.apiUrl = 'http://localhost:8000';
        this.stream = null;
        this.debugPanel = null;
        this.init();
    }
    
    init() {
        console.log('🚀 Done-Talking Extension loaded');
        this.createUI();
        this.createDebugPanel();
        this.setupMessageListener();
    }
    
    createUI() {
        const existingBtn = document.getElementById('done-talking-btn');
        if (existingBtn) existingBtn.remove();
        
        const button = document.createElement('div');
        button.id = 'done-talking-btn';
        button.innerHTML = '🎙️ Record';
        button.style.cssText = `
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            z-index: 999999 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            padding: 12px 20px !important;
            border-radius: 25px !important;
            cursor: pointer !important;
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            user-select: none !important;
        `;
        
        button.addEventListener('click', () => this.toggleRecording());
        document.body.appendChild(button);
    }
    
    createDebugPanel() {
        this.debugPanel = document.createElement('div');
        this.debugPanel.id = 'debug-panel';
        this.debugPanel.style.cssText = `
            position: fixed !important;
            top: 80px !important;
            right: 20px !important;
            z-index: 999998 !important;
            background: rgba(0, 0, 0, 0.9) !important;
            color: #00ff00 !important;
            padding: 15px !important;
            border-radius: 10px !important;
            font-family: monospace !important;
            font-size: 11px !important;
            max-width: 350px !important;
            min-width: 300px !important;
            line-height: 1.4 !important;
            display: none !important;
        `;
        
        this.debugPanel.innerHTML = `
            <div style="color: #ffff00; font-weight: bold; margin-bottom: 10px;">🔍 Audio Debug Panel</div>
            <div id="debug-content">Ready to debug...</div>
            <button onclick="this.parentElement.style.display='none'" style="margin-top: 10px; padding: 3px 8px; background: #333; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">Hide</button>
        `;
        
        document.body.appendChild(this.debugPanel);
    }
    
    updateDebugPanel(info) {
        if (!this.debugPanel) return;
        
        const content = document.getElementById('debug-content');
        if (content) {
            content.innerHTML = info;
        }
        this.debugPanel.style.display = 'block';
    }
    
    setupMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            switch (message.action) {
                case 'toggleRecording':
                    this.toggleRecording();
                    break;
                case 'getStatus':
                    sendResponse({isRecording: this.isRecording});
                    break;
            }
        });
    }
    
    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    
    async startRecording() {
        console.log('🎬 Starting recording...');
        this.updateDebugPanel('🎬 Starting recording...');
        
        try {
            // Step 1: Request display media
            console.log('📋 Requesting display media with audio...');
            this.updateDebugPanel(`
                📋 Requesting display media...<br>
                ⏳ Permission dialog should appear<br>
                ⚠️ Make sure to check "Share audio"!
            `);
            
            this.stream = await navigator.mediaDevices.getDisplayMedia({
                video: true,  // Include video to ensure dialog appears
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
            
            // Step 2: Analyze stream
            const audioTracks = this.stream.getAudioTracks();
            const videoTracks = this.stream.getVideoTracks();
            
            console.log('🎵 Audio tracks:', audioTracks.length);
            console.log('📹 Video tracks:', videoTracks.length);
            
            let debugInfo = `
                ✅ Stream obtained!<br>
                🎵 Audio tracks: <span style="color: ${audioTracks.length > 0 ? '#00ff00' : '#ff0000'}">${audioTracks.length}</span><br>
                📹 Video tracks: ${videoTracks.length}<br>
            `;
            
            if (audioTracks.length === 0) {
                debugInfo += `<br><span style="color: #ff0000">❌ NO AUDIO TRACKS!</span><br>
                💡 You need to check "Share audio" in the permission dialog<br>
                🔄 Click record again and make sure audio is enabled`;
                
                this.updateDebugPanel(debugInfo);
                this.showNotification('❌ No audio captured! Check "Share audio" checkbox', 'error');
                
                // Stop all tracks and return
                this.stream.getTracks().forEach(track => track.stop());
                return;
            }
            
            // Step 3: Audio track details
            audioTracks.forEach((track, index) => {
                console.log(`🎵 Audio track ${index}:`, {
                    label: track.label,
                    enabled: track.enabled,
                    muted: track.muted,
                    readyState: track.readyState
                });
                
                debugInfo += `<br>🎵 Track ${index}: ${track.label}<br>
                    └ Enabled: <span style="color: ${track.enabled ? '#00ff00' : '#ff0000'}">${track.enabled}</span><br>
                    └ Muted: <span style="color: ${track.muted ? '#ff0000' : '#00ff00'}">${track.muted}</span><br>
                    └ State: ${track.readyState}`;
            });
            
            // Step 4: Remove video tracks (we only want audio)
            videoTracks.forEach(track => {
                track.stop();
                this.stream.removeTrack(track);
            });
            debugInfo += `<br><br>📹 Removed ${videoTracks.length} video tracks`;
            
            // Step 5: Set up MediaRecorder
            const mimeType = 'audio/webm;codecs=opus';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                throw new Error('MIME type not supported: ' + mimeType);
            }
            
            this.recorder = new MediaRecorder(this.stream, {
                mimeType: mimeType,
                audioBitsPerSecond: 128000
            });
            
            this.audioChunks = [];
            let chunkCount = 0;
            let totalBytes = 0;
            
            this.recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    chunkCount++;
                    totalBytes += event.data.size;
                    
                    console.log(`📊 Audio chunk ${chunkCount}: ${event.data.size} bytes`);
                    
                    // Update debug panel with real-time stats
                    const realTimeInfo = debugInfo + `<br><br>📊 Recording Stats:<br>
                        └ Chunks: ${chunkCount}<br>
                        └ Total bytes: ${totalBytes}<br>
                        └ Latest chunk: ${event.data.size} bytes<br>
                        └ Status: <span style="color: #00ff00">🔴 RECORDING</span>`;
                    this.updateDebugPanel(realTimeInfo);
                } else {
                    console.warn('⚠️ Empty audio chunk received');
                }
            };
            
            this.recorder.onstop = () => {
                console.log('⏹️ Recording stopped');
                this.processAudio();
            };
            
            this.recorder.onerror = (event) => {
                console.error('❌ MediaRecorder error:', event.error);
                this.updateDebugPanel(debugInfo + `<br><br><span style="color: #ff0000">❌ Recording error: ${event.error.message}</span>`);
            };
            
            // Step 6: Start recording
            this.recorder.start(1000); // Collect chunks every second
            this.isRecording = true;
            
            console.log('✅ Recording started successfully');
            this.updateUI('recording');
            this.notifyBackground('recordingStarted');
            this.showNotification('🔴 Recording started! Watch debug panel for audio activity', 'success');
            
            // Update debug panel
            debugInfo += `<br><br>✅ Recording started!<br>
                📊 Collecting audio chunks every 1 second<br>
                🎵 Waiting for audio data...`;
            this.updateDebugPanel(debugInfo);
            
            // Step 7: Monitor audio levels (if possible)
            this.monitorAudioLevels();
            
            // Step 8: Handle stream end
            this.stream.getAudioTracks().forEach(track => {
                track.onended = () => {
                    console.log('🔚 Audio track ended');
                    if (this.isRecording) {
                        this.stopRecording();
                    }
                };
            });
            
        } catch (error) {
            console.error('❌ Recording failed:', error);
            this.updateDebugPanel(`<span style="color: #ff0000">❌ Recording failed:<br>${error.name}: ${error.message}</span>`);
            this.showNotification(`Recording failed: ${error.message}`, 'error');
        }
    }
    
    monitorAudioLevels() {
        // Try to create audio context to monitor levels
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(this.stream);
            const analyser = audioContext.createAnalyser();
            source.connect(analyser);
            
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            let silentCount = 0;
            const checkAudioLevel = () => {
                if (!this.isRecording) return;
                
                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                
                if (average < 1) {
                    silentCount++;
                } else {
                    silentCount = 0;
                }
                
                // Show warning if silent for too long
                if (silentCount > 10) { // 10 seconds of silence
                    console.warn('⚠️ No audio detected for 10+ seconds');
                }
                
                // Update debug with audio level
                const currentContent = document.getElementById('debug-content');
                if (currentContent && this.isRecording) {
                    const levelIndicator = `<br>🎚️ Audio level: ${Math.round(average)} ${average > 5 ? '🔊' : '🔇'}`;
                    if (!currentContent.innerHTML.includes('🎚️')) {
                        currentContent.innerHTML += levelIndicator;
                    } else {
                        currentContent.innerHTML = currentContent.innerHTML.replace(/🎚️.*/, levelIndicator);
                    }
                }
                
                setTimeout(checkAudioLevel, 1000);
            };
            
            checkAudioLevel();
            
        } catch (error) {
            console.warn('⚠️ Could not create audio monitor:', error);
        }
    }
    
    stopRecording() {
        if (this.recorder && this.isRecording) {
            console.log('⏹️ Stopping recording...');
            this.recorder.stop();
            this.isRecording = false;
            this.updateUI('processing');
            
            // Update debug panel
            this.updateDebugPanel(document.getElementById('debug-content').innerHTML.replace('🔴 RECORDING', '⏹️ STOPPED'));
        }
    }
    
    async processAudio() {
        console.log(`📊 Processing ${this.audioChunks.length} audio chunks`);
        
        if (this.audioChunks.length === 0) {
            console.warn('⚠️ No audio data to process');
            this.updateDebugPanel(document.getElementById('debug-content').innerHTML + `<br><br><span style="color: #ff0000">❌ No audio data recorded!</span>`);
            this.showNotification('No audio data recorded', 'error');
            this.updateUI('ready');
            return;
        }
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        console.log(`📁 Audio blob size: ${audioBlob.size} bytes`);
        
        // Update debug panel with final stats
        let finalDebugInfo = document.getElementById('debug-content').innerHTML;
        finalDebugInfo += `<br><br>📁 Final Results:<br>
            └ Total chunks: ${this.audioChunks.length}<br>
            └ Final blob size: ${audioBlob.size} bytes<br>
            └ Duration estimate: ~${Math.round(this.audioChunks.length)} seconds`;
        
        if (audioBlob.size < 1000) {
            finalDebugInfo += `<br><span style="color: #ff0000">⚠️ File very small - likely no audio!</span>`;
        } else {
            finalDebugInfo += `<br><span style="color: #00ff00">✅ Good file size - likely has audio!</span>`;
        }
        
        this.updateDebugPanel(finalDebugInfo);
        
        // Process the audio
        const formData = new FormData();
        formData.append('audio', audioBlob, `meeting_${Date.now()}.webm`);
        formData.append('platform', this.detectPlatform());
        formData.append('timestamp', new Date().toISOString());
        
        try {
            const response = await fetch(`${this.apiUrl}/api/audio/process`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                this.showNotification('Recording sent to Done-Talking!', 'success');
            } else {
                throw new Error(`API returned ${response.status}`);
            }
        } catch (error) {
            console.warn('⚠️ API not available, downloading file:', error);
            this.downloadAudio(audioBlob);
            this.showNotification('Recording downloaded for processing', 'success');
        }
        
        this.updateUI('ready');
        this.notifyBackground('recordingStopped');
        
        // Clean up stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }
    
    detectPlatform() {
        const hostname = window.location.hostname;
        if (hostname.includes('meet.google.com')) return 'google-meet';
        if (hostname.includes('zoom.us')) return 'zoom';
        if (hostname.includes('teams.microsoft.com')) return 'teams';
        if (hostname.includes('webex.com')) return 'webex';
        return 'unknown';
    }
    
    downloadAudio(audioBlob) {
        const url = URL.createObjectURL(audioBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `meeting_${Date.now()}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('💾 Audio file downloaded');
    }
    
    updateUI(state) {
        const button = document.getElementById('done-talking-btn');
        if (!button) return;
        
        switch(state) {
            case 'recording':
                button.innerHTML = '⏹️ Stop';
                button.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)';
                break;
            case 'processing':
                button.innerHTML = '⏳ Processing';
                button.style.background = 'linear-gradient(135deg, #feca57 0%, #ff9ff3 100%)';
                break;
            default:
                button.innerHTML = '🎙️ Record';
                button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    }
    
    showNotification(message, type) {
        console.log(`📢 ${type}: ${message}`);
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed !important;
            top: 70px !important;
            right: 380px !important;
            z-index: 999997 !important;
            padding: 10px 15px !important;
            border-radius: 20px !important;
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 12px !important;
            max-width: 250px !important;
            ${type === 'success' ? 'background: rgba(76, 175, 80, 0.95) !important; color: white !important;' : ''}
            ${type === 'error' ? 'background: rgba(244, 67, 54, 0.95) !important; color: white !important;' : ''}
            ${type === 'warning' ? 'background: rgba(255, 193, 7, 0.95) !important; color: #333 !important;' : ''}
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 5000);
    }
    
    notifyBackground(action) {
        try {
            chrome.runtime.sendMessage({action: action});
        } catch (error) {
            console.warn('⚠️ Could not notify background:', error);
        }
    }
}

// Initialize
new DoneTalkingRecorder();