class DoneTalkingRecorder {
    constructor() {
        this.isRecording = false;
        this.recorder = null;
        this.audioChunks = [];
        this.apiUrl = 'http://localhost:8000/v2';
        this.apiKey = null;
        this.micStream = null;
        this.systemStream = null;
        this.finalStream = null;
        this.debugPanel = null;
        this.audioContext = null;
        this.startTime = null;
        this.init();
    }
    
    async init() {
        console.log('🚀 Done-Talking Extension loaded');
        await this.loadApiKey(); // Load token from storage
        this.createUI();
        this.createDebugPanel();
        this.setupMessageListener();
    }
    
    async loadApiKey() {
        // Load API key from Chrome storage
        return new Promise((resolve) => {
            chrome.storage.sync.get(['apiToken'], (result) => {
                this.apiKey = result.apiToken || 'YOUR_DEFAULT_TOKEN'; // Fallback
                console.log('API token loaded');
                resolve();
            });
        });
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
                    sendResponse({
                        isRecording: this.isRecording,
                        startTime: this.startTime,
                        platform: this.detectPlatform()
                    });
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
        this.updateDebugPanel('🎬 Starting audio capture...');
        
        try {
            // Reset streams
            this.micStream = null;
            this.systemStream = null;
            this.finalStream = null;
            
            let debugInfo = '🎵 Audio Capture Strategy:<br>';
            
            // Strategy 1: Always get microphone (most reliable)
            try {
                console.log('🎙️ Requesting microphone...');
                debugInfo += '🎙️ Microphone: Requesting...<br>';
                
                this.micStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        sampleRate: 44100,
                        channelCount: 2
                    }
                });
                
                debugInfo += '✅ Microphone: Success!<br>';
                console.log('✅ Microphone stream obtained');
                
                // Test microphone stream
                const micTracks = this.micStream.getAudioTracks();
                debugInfo += `└ Tracks: ${micTracks.length}<br>`;
                micTracks.forEach((track, i) => {
                    debugInfo += `└ Track ${i}: ${track.label} (${track.readyState})<br>`;
                });
                
            } catch (micError) {
                console.error('❌ Microphone failed:', micError);
                debugInfo += `❌ Microphone: Failed (${micError.name})<br>`;
                this.showNotification('❌ Microphone access denied! Please allow microphone access.', 'error');
                return;
            }
            
            // Strategy 2: Try to get tab audio (optional enhancement)
            try {
                console.log('🔊 Requesting tab audio...');
                debugInfo += '🔊 Tab Audio: Requesting...<br>';
                
                // Request tab audio with explicit instructions
                this.systemStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { mediaSource: 'tab' },
                    audio: {
                        echoCancellation: false,
                        noiseSuppression: false,
                        autoGainControl: false,
                        sampleRate: 44100
                    }
                });
                
                // Remove video track immediately
                const videoTracks = this.systemStream.getVideoTracks();
                videoTracks.forEach(track => {
                    track.stop();
                    this.systemStream.removeTrack(track);
                });
                
                const systemAudioTracks = this.systemStream.getAudioTracks();
                if (systemAudioTracks.length > 0) {
                    debugInfo += '✅ Tab Audio: Success!<br>';
                    debugInfo += `└ Tracks: ${systemAudioTracks.length}<br>`;
                    console.log('✅ Tab audio obtained');
                } else {
                    debugInfo += '⚠️ Tab Audio: No audio shared<br>';
                    this.systemStream = null;
                }
                
            } catch (systemError) {
                console.warn('⚠️ Tab audio failed:', systemError);
                debugInfo += '⚠️ Tab Audio: Not available<br>';
                this.systemStream = null;
            }
            
            // Strategy 3: Create final recording stream
            debugInfo += '<br>🔗 Creating Recording Stream:<br>';
            
            if (this.systemStream && this.systemStream.getAudioTracks().length > 0) {
                // If we have both mic and system audio, combine them
                console.log('🔀 Combining microphone and system audio');
                debugInfo += '🔀 Combining mic + system audio<br>';
                
                try {
                    // Create AudioContext to mix streams
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const destination = this.audioContext.createMediaStreamDestination();
                    
                    // Add microphone
                    const micSource = this.audioContext.createMediaStreamSource(this.micStream);
                    const micGain = this.audioContext.createGain();
                    micGain.gain.value = 1.0; // Full microphone volume
                    micSource.connect(micGain);
                    micGain.connect(destination);
                    
                    // Add system audio
                    const systemSource = this.audioContext.createMediaStreamSource(this.systemStream);
                    const systemGain = this.audioContext.createGain();
                    systemGain.gain.value = 0.8; // Slightly lower system audio to avoid feedback
                    systemSource.connect(systemGain);
                    systemGain.connect(destination);
                    
                    this.finalStream = destination.stream;
                    debugInfo += '✅ Mixed stream created<br>';
                    
                } catch (mixError) {
                    console.warn('⚠️ Audio mixing failed, using microphone only:', mixError);
                    debugInfo += '⚠️ Mixing failed, using mic only<br>';
                    this.finalStream = this.micStream;
                }
            } else {
                // Use microphone only
                console.log('🎙️ Using microphone only');
                debugInfo += '🎙️ Using microphone only<br>';
                this.finalStream = this.micStream;
            }
            
            // Verify final stream
            const finalTracks = this.finalStream.getAudioTracks();
            if (finalTracks.length === 0) {
                throw new Error('No audio tracks in final stream');
            }
            
            debugInfo += `✅ Final stream: ${finalTracks.length} tracks<br>`;
            
            // Test each track
            finalTracks.forEach((track, i) => {
                debugInfo += `└ Track ${i}: ${track.enabled ? '🟢' : '🔴'} ${track.label}<br>`;
                console.log(`Track ${i}:`, {
                    label: track.label,
                    enabled: track.enabled,
                    muted: track.muted,
                    readyState: track.readyState
                });
            });
            
            // Strategy 4: Set up MediaRecorder with fallback MIME types
            debugInfo += '<br>📼 Setting up recorder:<br>';
            
            const mimeTypes = [
                'audio/webm;codecs=opus',
                'audio/webm',
                'audio/mp4',
                'audio/ogg',
                ''
            ];
            
            let selectedMimeType = '';
            for (const type of mimeTypes) {
                if (!type || MediaRecorder.isTypeSupported(type)) {
                    selectedMimeType = type;
                    break;
                }
            }
            
            debugInfo += `📼 MIME type: ${selectedMimeType || 'browser default'}<br>`;
            console.log('📼 Using MIME type:', selectedMimeType);
            
            const recordingOptions = {
                audioBitsPerSecond: 128000
            };
            
            if (selectedMimeType) {
                recordingOptions.mimeType = selectedMimeType;
            }
            
            this.recorder = new MediaRecorder(this.finalStream, recordingOptions);
            
            // Set up recording event handlers
            this.audioChunks = [];
            let chunkCount = 0;
            let totalSize = 0;
            
            this.recorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    chunkCount++;
                    totalSize += event.data.size;
                    
                    console.log(`📊 Chunk ${chunkCount}: ${event.data.size} bytes`);
                    
                    // Update debug with chunk info
                    const currentContent = document.getElementById('debug-content');
                    if (currentContent) {
                        const chunkInfo = `<br>📊 Chunks: ${chunkCount} (${Math.round(totalSize/1024)}KB)`;
                        if (currentContent.innerHTML.includes('📊')) {
                            currentContent.innerHTML = currentContent.innerHTML.replace(/📊.*/, chunkInfo);
                        } else {
                            currentContent.innerHTML += chunkInfo;
                        }
                    }
                } else {
                    console.warn('⚠️ Empty chunk received');
                }
            };
            
            this.recorder.onstop = () => {
                console.log('⏹️ Recording stopped');
                this.processAudio();
            };
            
            this.recorder.onerror = (event) => {
                console.error('❌ Recording error:', event.error);
                this.showNotification(`Recording error: ${event.error.message}`, 'error');
            };
            
            // Strategy 5: Start recording with frequent data collection
            console.log('▶️ Starting MediaRecorder...');
            this.recorder.start(100); // Collect data every 100ms for immediate feedback
            this.isRecording = true;
            this.startTime = new Date();
            
            debugInfo += '▶️ Recording started!<br>';
            this.updateDebugPanel(debugInfo);
            
            // UI updates
            this.updateUI('recording');
            this.notifyBackground('recordingStarted');
            this.showNotification('🔴 Recording started! Microphone active', 'success');
            
            // Monitor audio levels
            this.startAudioMonitoring();
            
            // Set up cleanup on track end
            this.finalStream.getAudioTracks().forEach(track => {
                track.onended = () => {
                    console.log('🔚 Audio track ended');
                    if (this.isRecording) {
                        this.stopRecording();
                    }
                };
            });
            
        } catch (error) {
            console.error('❌ Recording setup failed:', error);
            this.updateDebugPanel(`<span style="color: #ff0000">❌ Recording failed:<br>${error.name}: ${error.message}</span>`);
            this.showNotification(`Recording failed: ${error.message}`, 'error');
            this.cleanup();
        }
    }
    
    startAudioMonitoring() {
        if (!this.finalStream) return;
        
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            const source = this.audioContext.createMediaStreamSource(this.finalStream);
            const analyser = this.audioContext.createAnalyser();
            source.connect(analyser);
            
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            let maxLevel = 0;
            let silentCount = 0;
            
            const checkLevels = () => {
                if (!this.isRecording) return;
                
                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                const level = Math.round(average);
                
                if (level > maxLevel) maxLevel = level;
                
                if (level < 2) {
                    silentCount++;
                } else {
                    silentCount = 0;
                }
                
                // Update debug with audio level
                const currentContent = document.getElementById('debug-content');
                if (currentContent) {
                    const levelInfo = `<br>🎚️ Audio: ${level} (max: ${maxLevel}) ${level > 5 ? '🔊' : '🔇'}`;
                    if (currentContent.innerHTML.includes('🎚️')) {
                        currentContent.innerHTML = currentContent.innerHTML.replace(/🎚️.*/, levelInfo);
                    } else {
                        currentContent.innerHTML += levelInfo;
                    }
                }
                
                // Warn if too silent
                if (silentCount > 5) {
                    console.warn('⚠️ Audio appears silent for 5+ seconds');
                }
                
                setTimeout(checkLevels, 1000);
            };
            
            checkLevels();
            
        } catch (error) {
            console.warn('⚠️ Audio monitoring failed:', error);
        }
    }
    
    stopRecording() {
        if (this.recorder && this.isRecording) {
            console.log('⏹️ Stopping recording...');
            this.recorder.stop();
            this.isRecording = false;
            this.updateUI('processing');
            
            // Update debug
            const currentContent = document.getElementById('debug-content');
            if (currentContent) {
                currentContent.innerHTML += '<br>⏹️ Recording stopped, processing...';
            }
        }
    }
    
    async processAudio() {
        console.log(`📊 Processing ${this.audioChunks.length} audio chunks`);
        
        if (this.audioChunks.length === 0) {
            console.warn('⚠️ No audio data to process');
            this.showNotification('No audio data recorded', 'error');
            this.updateUI('ready');
            this.cleanup();
            return;
        }
        
        const audioBlob = new Blob(this.audioChunks, { 
            type: this.recorder.mimeType || 'audio/webm' 
        });
        
        console.log(`📁 Audio blob: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
        
        // Update debug with results
        const duration = this.startTime ? (Date.now() - this.startTime.getTime()) / 1000 : 0;
        const currentContent = document.getElementById('debug-content');
        if (currentContent) {
            currentContent.innerHTML += `<br><br>📁 Results:<br>
                └ File size: ${Math.round(audioBlob.size/1024)}KB<br>
                └ Duration: ${Math.round(duration)}s<br>
                └ Chunks: ${this.audioChunks.length}<br>
                └ Type: ${audioBlob.type}`;
        }
        
        // Create FormData for upload
        const formData = new FormData();
        const filename = `meeting_${Date.now()}.${audioBlob.type.includes('mp4') ? 'm4a' : 'webm'}`;
        formData.append('audio_file', audioBlob, filename);
        formData.append('platform', this.detectPlatform());
        formData.append('timestamp', new Date().toISOString());
        formData.append('duration', duration.toString());
        
        try {
            const response = await fetch(`${this.apiUrl}/receive_meeting`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`  
                },
                body: formData
            });
            
            if (response.ok) {
                this.showNotification('✅ Recording uploaded successfully!', 'success');
                console.log('✅ Upload successful');
            } else {
                throw new Error(`Upload failed: ${response.status}`);
            }
        } catch (error) {
            console.warn('⚠️ Upload failed, downloading locally:', error);
            this.downloadAudio(audioBlob, filename);
            this.showNotification('📥 Recording saved locally for manual upload', 'info');
        }
        
        this.updateUI('ready');
        this.notifyBackground('recordingStopped');
        this.cleanup();
    }
    
    downloadAudio(audioBlob, filename) {
        const url = URL.createObjectURL(audioBlob);

        // Use Chrome Downloads API to save to custom directory
        chrome.downloads.download({
            url: url,
            filename: `Done-Talking/assets/recorded_meetings/${filename}`,
            saveAs: false // Auto-save to Downloads/Done-Talking-Recordings/
        }, (downloadId) => {
            if (chrome.runtime.lastError) {
                console.warn('⚠️ Chrome downloads API failed, falling back to default method:', chrome.runtime.lastError);
                // Fallback to original method
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            } else {
                console.log('💾 Audio file saved to Done-Talking-Recordings folder:', filename);
            }

            // Clean up the object URL
            URL.revokeObjectURL(url);
        });
    }
    
    cleanup() {
        // Clean up streams
        if (this.micStream) {
            this.micStream.getTracks().forEach(track => track.stop());
            this.micStream = null;
        }
        
        if (this.systemStream) {
            this.systemStream.getTracks().forEach(track => track.stop());
            this.systemStream = null;
        }
        
        if (this.finalStream && this.finalStream !== this.micStream) {
            this.finalStream.getTracks().forEach(track => track.stop());
            this.finalStream = null;
        }
        
        // Clean up audio context
        if (this.audioContext && this.audioContext.state !== 'closed') {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        console.log('🧹 Cleanup completed');
    }
    
    detectPlatform() {
        const hostname = window.location.hostname;
        if (hostname.includes('meet.google.com')) return 'google-meet';
        if (hostname.includes('zoom.us')) return 'zoom';
        if (hostname.includes('teams.microsoft.com')) return 'teams';
        if (hostname.includes('webex.com')) return 'webex';
        return 'unknown';
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
            ${type === 'info' ? 'background: rgba(33, 150, 243, 0.95) !important; color: white !important;' : ''}
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