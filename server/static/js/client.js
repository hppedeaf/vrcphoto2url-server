/**
 * Custom Server File Manager - Client Interface
 * Modern web-based client interface with drag-and-drop file upload,
 * real-time connection management, and settings persistence.
 */

class FileManagerClient {
    constructor() {
        this.serverUrl = localStorage.getItem('server_url') || '';
        this.apiKey = localStorage.getItem('api_key') || '';
        this.isConnected = false;
        this.isMonitoring = false;
        this.uploadStats = {
            totalUploads: 0,
            totalSize: 0,
            successRate: 100,
            averageSpeed: 0
        };
        this.uploadHistory = [];
        this.currentTheme = localStorage.getItem('client_theme') || 'green';
        
        this.init();
    }    init() {
        console.log('FileManagerClient initializing...');
        this.setupEventListeners();
        this.loadSettings();
        this.hideLoadingScreen();
        this.applyTheme();
        this.logActivity('🌟 Client interface loaded successfully');
        
        // Auto-connect if we have saved credentials
        if (this.serverUrl) {
            this.testConnection(true);
        }
        console.log('FileManagerClient initialized successfully');
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 300);
            }
        }, 1000);
    }

    setupEventListeners() {
        // File upload handlers
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const browseBtn = document.getElementById('browse-btn');

        // Drag and drop
        dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        dropZone.addEventListener('drop', this.handleDrop.bind(this));
        dropZone.addEventListener('click', () => fileInput.click());

        // File input
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        browseBtn.addEventListener('click', () => fileInput.click());

        // Header buttons
        document.getElementById('connect-btn').addEventListener('click', this.showConnectionModal.bind(this));
        document.getElementById('monitor-btn').addEventListener('click', this.toggleMonitoring.bind(this));
        document.getElementById('settings-btn').addEventListener('click', this.showSettingsModal.bind(this));        // Tab navigation
        console.log('Setting up tab navigation...');
        const tabButtons = document.querySelectorAll('.tab-btn');
        console.log(`Found ${tabButtons.length} tab buttons`);
        
        tabButtons.forEach(btn => {
            console.log('Adding listener to tab:', btn.dataset.tab);
            btn.addEventListener('click', (e) => {
                console.log('Tab clicked:', e.target.dataset.tab);
                try {
                    this.switchTab(e.target.dataset.tab);
                } catch (error) {
                    console.error('Switch tab error:', error);
                }
            });
        });

        // Connection modal
        this.setupConnectionModal();
        this.setupSettingsModal();

        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupConnectionModal() {
        const modal = document.getElementById('connection-modal');
        const form = document.getElementById('connection-form');
        const testBtn = document.getElementById('test-connection-btn');
        const closeBtn = modal.querySelector('.modal-close');

        form.addEventListener('submit', this.handleConnectionSubmit.bind(this));
        testBtn.addEventListener('click', this.testConnection.bind(this));
        closeBtn.addEventListener('click', () => this.closeModal(modal));

        // Load saved values
        document.getElementById('server-url').value = this.serverUrl;
        document.getElementById('api-key').value = this.apiKey;
        document.getElementById('remember-connection').checked = !!localStorage.getItem('remember_connection');
    }

    setupSettingsModal() {
        const modal = document.getElementById('settings-modal');
        const closeBtn = modal.querySelector('.modal-close');
        const saveBtn = document.getElementById('save-settings-btn');
        const resetBtn = document.getElementById('reset-settings-btn');

        closeBtn.addEventListener('click', () => this.closeModal(modal));
        saveBtn.addEventListener('click', this.saveSettings.bind(this));
        resetBtn.addEventListener('click', this.resetSettings.bind(this));

        // Theme preset buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const preset = e.target.dataset.preset;
                this.setTheme(preset);
            });
        });
    }

    // File Upload Handlers
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropZone = document.getElementById('drop-zone');
        dropZone.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropZone = document.getElementById('drop-zone');
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropZone = document.getElementById('drop-zone');
        dropZone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            this.uploadFiles(files);
        }
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            this.uploadFiles(files);
        }
    }

    async uploadFiles(files) {
        if (!this.isConnected) {
            this.showNotification('❌ Please connect to server first', 'error');
            return;
        }

        if (files.length === 0) return;

        this.showProgress();
        this.logActivity(`📤 Starting upload of ${files.length} file(s)`);

        const totalFiles = files.length;
        let uploadedFiles = 0;
        let totalBytes = 0;
        let uploadedBytes = 0;

        // Calculate total size
        files.forEach(file => totalBytes += file.size);

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            try {
                this.updateProgress(
                    `Uploading ${file.name} (${i + 1}/${totalFiles})`,
                    (uploadedBytes / totalBytes) * 100
                );

                const result = await this.uploadSingleFile(file);
                
                if (result.success) {
                    uploadedFiles++;
                    uploadedBytes += file.size;
                    this.addFileToHistory(result);
                    this.logActivity(`✅ ${file.name} uploaded successfully`);
                    
                    // Auto-copy URL to clipboard if enabled
                    if (this.getSetting('auto-clipboard')) {
                        await navigator.clipboard.writeText(result.url);
                    }
                } else {
                    this.logActivity(`❌ Failed to upload ${file.name}: ${result.message}`);
                }

                this.updateProgress(
                    `Uploading ${file.name} (${i + 1}/${totalFiles})`,
                    (uploadedBytes / totalBytes) * 100
                );

            } catch (error) {
                this.logActivity(`❌ Error uploading ${file.name}: ${error.message}`);
            }
        }

        this.hideProgress();
        this.updateStats(uploadedFiles, uploadedBytes, totalFiles);
        
        if (uploadedFiles === totalFiles) {
            this.showNotification(`✅ Successfully uploaded ${uploadedFiles} file(s)`, 'success');
        } else {
            this.showNotification(`⚠️ Uploaded ${uploadedFiles}/${totalFiles} files`, 'warning');
        }

        this.refreshFilesList();
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.serverUrl}/upload`, {
            method: 'POST',
            headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {},
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    // Connection Management
    async handleConnectionSubmit(e) {
        e.preventDefault();
        
        const serverUrl = document.getElementById('server-url').value.trim();
        const apiKey = document.getElementById('api-key').value.trim();
        const remember = document.getElementById('remember-connection').checked;

        if (!serverUrl) {
            this.showNotification('❌ Please enter a server URL', 'error');
            return;
        }

        this.serverUrl = serverUrl;
        this.apiKey = apiKey;

        if (remember) {
            localStorage.setItem('server_url', serverUrl);
            localStorage.setItem('api_key', apiKey);
            localStorage.setItem('remember_connection', 'true');
        }

        const connected = await this.testConnection();
        if (connected) {
            this.closeModal(document.getElementById('connection-modal'));
        }
    }

    async testConnection(silent = false) {
        if (!this.serverUrl) {
            if (!silent) this.showNotification('❌ Please enter a server URL', 'error');
            return false;
        }

        try {
            if (!silent) this.logActivity('🔄 Testing connection...');
            
            const response = await fetch(`${this.serverUrl}/health`, {
                method: 'GET',
                headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
            });

            if (response.ok) {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                if (!silent) {
                    this.showNotification('✅ Connected to server successfully', 'success');
                    this.logActivity('✅ Connected to server successfully');
                }
                return true;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            if (!silent) {
                this.showNotification(`❌ Connection failed: ${error.message}`, 'error');
                this.logActivity(`❌ Connection failed: ${error.message}`);
            }
            return false;
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        const connectBtn = document.getElementById('connect-btn');
        const monitorBtn = document.getElementById('monitor-btn');

        if (connected) {
            statusElement.innerHTML = '<span class="status-icon">✅</span><span class="status-text">Connected</span>';
            statusElement.classList.add('connected');
            connectBtn.querySelector('.btn-text').textContent = 'Disconnect';
            monitorBtn.disabled = false;
        } else {
            statusElement.innerHTML = '<span class="status-icon">❌</span><span class="status-text">Not Connected</span>';
            statusElement.classList.remove('connected');
            connectBtn.querySelector('.btn-text').textContent = 'Connect';
            monitorBtn.disabled = true;
            this.isMonitoring = false;
            this.updateMonitoringStatus(false);
        }
    }

    toggleMonitoring() {
        if (!this.isConnected) {
            this.showNotification('❌ Please connect to server first', 'error');
            return;
        }

        this.isMonitoring = !this.isMonitoring;
        this.updateMonitoringStatus(this.isMonitoring);

        if (this.isMonitoring) {
            this.showNotification('👁️ Folder monitoring started', 'info');
            this.logActivity('👁️ Folder monitoring started');
        } else {
            this.showNotification('⏹️ Folder monitoring stopped', 'info');
            this.logActivity('⏹️ Folder monitoring stopped');
        }
    }

    updateMonitoringStatus(monitoring) {
        const statusElement = document.getElementById('monitoring-status');
        const monitorBtn = document.getElementById('monitor-btn');

        if (monitoring) {
            statusElement.innerHTML = '<span class="status-icon">👁️</span><span class="status-text">Monitoring</span>';
            statusElement.classList.add('monitoring');
            monitorBtn.querySelector('.btn-text').textContent = 'Stop Monitor';
        } else {
            statusElement.innerHTML = '<span class="status-icon">📁</span><span class="status-text">Not Monitoring</span>';
            statusElement.classList.remove('monitoring');
            monitorBtn.querySelector('.btn-text').textContent = 'Monitor';
        }
    }

    // UI Management
    showConnectionModal() {
        if (this.isConnected) {
            // Disconnect
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.showNotification('🔌 Disconnected from server', 'info');
            this.logActivity('🔌 Disconnected from server');
        } else {
            // Show connection modal
            document.getElementById('connection-modal').style.display = 'flex';
        }
    }

    showSettingsModal() {
        this.loadSettingsToModal();
        document.getElementById('settings-modal').style.display = 'flex';
    }

    closeModal(modal) {
        modal.style.display = 'none';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    showProgress() {
        const progressSection = document.getElementById('progress-section');
        progressSection.style.display = 'block';
    }

    hideProgress() {
        const progressSection = document.getElementById('progress-section');
        setTimeout(() => {
            progressSection.style.display = 'none';
        }, 2000);
    }

    updateProgress(label, percentage) {
        document.getElementById('progress-label').textContent = label;
        document.getElementById('progress-fill').style.width = `${percentage}%`;
        document.getElementById('progress-percentage').textContent = `${Math.round(percentage)}%`;
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    logActivity(message) {
        const activityLog = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString();
        
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <span class="activity-time">${timestamp}</span>
            <span class="activity-text">${message}</span>
        `;

        activityLog.insertBefore(activityItem, activityLog.firstChild);

        // Keep only last 50 entries
        while (activityLog.children.length > 50) {
            activityLog.removeChild(activityLog.lastChild);
        }
    }

    // Settings Management
    loadSettings() {
        const settings = {
            'auto-upload-enabled': true,
            'auto-clipboard': true,
            'auto-resize': false,
            'max-resolution': 2048
        };

        Object.keys(settings).forEach(key => {
            const saved = localStorage.getItem(`setting_${key}`);
            if (saved !== null) {
                settings[key] = saved === 'true' || (!isNaN(saved) ? parseInt(saved) : saved);
            }
        });

        this.settings = settings;
    }

    loadSettingsToModal() {
        document.getElementById('auto-upload-enabled').checked = this.getSetting('auto-upload-enabled');
        document.getElementById('auto-clipboard').checked = this.getSetting('auto-clipboard');
        document.getElementById('auto-resize').checked = this.getSetting('auto-resize');
        document.getElementById('max-resolution').value = this.getSetting('max-resolution');

        // Update theme buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-preset="${this.currentTheme}"]`).classList.add('active');
    }

    saveSettings() {
        const settings = {
            'auto-upload-enabled': document.getElementById('auto-upload-enabled').checked,
            'auto-clipboard': document.getElementById('auto-clipboard').checked,
            'auto-resize': document.getElementById('auto-resize').checked,
            'max-resolution': parseInt(document.getElementById('max-resolution').value)
        };

        Object.keys(settings).forEach(key => {
            localStorage.setItem(`setting_${key}`, settings[key]);
            this.settings[key] = settings[key];
        });

        this.showNotification('✅ Settings saved successfully', 'success');
        this.closeModal(document.getElementById('settings-modal'));
    }

    resetSettings() {
        localStorage.removeItem('setting_auto-upload-enabled');
        localStorage.removeItem('setting_auto-clipboard');
        localStorage.removeItem('setting_auto-resize');
        localStorage.removeItem('setting_max-resolution');
        
        this.loadSettings();
        this.loadSettingsToModal();
        this.showNotification('🔄 Settings reset to defaults', 'info');
    }

    getSetting(key) {
        return this.settings[key];
    }

    // Theme Management
    setTheme(theme) {
        this.currentTheme = theme;
        localStorage.setItem('client_theme', theme);
        this.applyTheme();
        
        // Update button state
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-preset="${theme}"]`).classList.add('active');
        
        this.showNotification(`🎨 Theme changed to ${theme}`, 'success');
    }

    applyTheme() {
        document.body.className = `theme-${this.currentTheme}`;
    }

    // File Management
    addFileToHistory(fileResult) {
        this.uploadHistory.unshift({
            ...fileResult,
            uploadTime: new Date().toISOString()
        });

        // Keep only last 100 files
        if (this.uploadHistory.length > 100) {
            this.uploadHistory.pop();
        }
    }

    refreshFilesList() {
        const filesList = document.getElementById('files-list');
        
        if (this.uploadHistory.length === 0) {
            filesList.innerHTML = `
                <div class="files-empty">
                    <span class="empty-icon">📁</span>
                    <span class="empty-text">No files uploaded yet</span>
                </div>
            `;
            return;
        }

        filesList.innerHTML = this.uploadHistory.slice(0, 20).map(file => `
            <div class="file-item">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">${file.original_filename}</div>
                    <div class="file-meta">${this.formatFileSize(file.file_size)} • ${new Date(file.uploadTime).toLocaleString()}</div>
                </div>
                <div class="file-actions">
                    <button class="file-action-btn" onclick="navigator.clipboard.writeText('${file.url}')">📋</button>
                    <button class="file-action-btn" onclick="window.open('${file.url}', '_blank')">🔗</button>
                </div>
            </div>
        `).join('');
    }

    updateStats(uploadedFiles, uploadedBytes, totalFiles) {
        this.uploadStats.totalUploads += uploadedFiles;
        this.uploadStats.totalSize += uploadedBytes;
        this.uploadStats.successRate = Math.round((uploadedFiles / totalFiles) * 100);

        document.getElementById('total-uploads').textContent = this.uploadStats.totalUploads;
        document.getElementById('total-size').textContent = this.formatFileSize(this.uploadStats.totalSize);
        document.getElementById('success-rate').textContent = `${this.uploadStats.successRate}%`;
        document.getElementById('avg-speed').textContent = `${(this.uploadStats.averageSpeed / 1024 / 1024).toFixed(1)} MB/s`;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the client when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.fileManagerClient = new FileManagerClient();
});
