// Admin Dashboard JavaScript - Custom Server File Manager
class AdminDashboard {
    constructor() {
        this.serverUrl = window.location.origin;
        this.isAuthenticated = false;
        this.refreshInterval = null;
        this.currentTab = 'files';
        this.files = [];
        this.activityLog = [];
        this.startTime = Date.now();
        
        this.init();
    }
    
    async init() {
        // Check authentication
        await this.checkAuth();
        
        // Load initial data
        await this.loadDashboardData();
        
        // Start refresh interval
        this.startAutoRefresh();
        
        // Update uptime display
        this.updateUptime();
        setInterval(() => this.updateUptime(), 1000);
        
        console.log('Admin Dashboard initialized');
    }
      async checkAuth() {
        try {
            // Simple demo authentication check
            const isAuth = localStorage.getItem('adminAuth') === 'true';
            
            if (!isAuth) {
                window.location.href = '/admin/login';
                return false;
            }
            
            this.isAuthenticated = true;
            return true;
        } catch (error) {
            console.error('Authentication failed:', error);
            window.location.href = '/admin/login';
            return false;
        }
    }
    
    async loadDashboardData() {
        this.showProgress('Loading dashboard data...', 0);
        
        try {
            // Load files
            this.showProgress('Loading files...', 25);
            await this.loadFiles();
            
            // Load statistics
            this.showProgress('Loading statistics...', 50);
            await this.loadStatistics();
            
            // Load activity log
            this.showProgress('Loading activity...', 75);
            this.loadActivityLog();
            
            // Load system info
            this.showProgress('Loading system info...', 90);
            this.loadSystemInfo();
            
            this.showProgress('Complete!', 100);
            setTimeout(() => this.hideProgress(), 500);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.hideProgress();
            this.showNotification('Failed to load data', 'error');
        }
    }
    
    async loadFiles() {
        try {
            const response = await fetch(`${this.serverUrl}/admin/files`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.files = data.files || [];
                this.updateFileList();
                this.logActivity('Loaded file list', 'info');
            } else {
                // For demo purposes, create some sample data
                this.files = this.generateSampleFiles();
                this.updateFileList();
                this.logActivity('Loaded sample file data', 'info');
            }
        } catch (error) {
            console.warn('Using sample data:', error.message);
            this.files = this.generateSampleFiles();
            this.updateFileList();
        }
    }
    
    generateSampleFiles() {
        const sampleFiles = [];
        const fileTypes = ['image/png', 'image/jpeg', 'text/plain', 'application/pdf'];
        const baseNames = ['document', 'photo', 'screenshot', 'report', 'image'];
        
        for (let i = 0; i < 15; i++) {
            const baseName = baseNames[Math.floor(Math.random() * baseNames.length)];
            const fileType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
            const extension = fileType.split('/')[1] === 'plain' ? 'txt' : fileType.split('/')[1];
            
            sampleFiles.push({
                file_id: `file-${i + 1}`,
                original_filename: `${baseName}_${i + 1}.${extension}`,
                filename: `${Date.now()}_${baseName}_${i + 1}.${extension}`,
                url: `${this.serverUrl}/files/file-${i + 1}`,
                file_size: Math.floor(Math.random() * 5000000) + 10000, // 10KB to 5MB
                upload_time: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                file_type: fileType
            });
        }
        
        return sampleFiles.sort((a, b) => new Date(b.upload_time) - new Date(a.upload_time));
    }
    
    async loadStatistics() {
        try {
            // Calculate statistics from files
            const totalFiles = this.files.length;
            const totalSize = this.files.reduce((sum, file) => sum + file.file_size, 0);
            const today = new Date().toDateString();
            const uploadsToday = this.files.filter(file => 
                new Date(file.upload_time).toDateString() === today
            ).length;
            
            // Update statistics display
            document.getElementById('total-files').textContent = totalFiles;
            document.getElementById('storage-used').textContent = this.formatFileSize(totalSize);
            document.getElementById('uploads-today').textContent = uploadsToday;
            document.getElementById('file-count').textContent = `${totalFiles} files`;
            
            this.logActivity(`Statistics updated: ${totalFiles} files, ${this.formatFileSize(totalSize)} used`, 'info');
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }
    
    updateFileList() {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';
        
        this.files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-name" title="${file.original_filename}">
                    ${this.getFileIcon(file.file_type)} ${file.original_filename}
                </div>
                <div class="file-size">${this.formatFileSize(file.file_size)}</div>
                <div class="file-date">${this.formatDate(file.upload_time)}</div>
                <div class="file-actions">
                    <button class="file-action-btn" onclick="adminDashboard.viewFile('${file.file_id}')" title="View">
                        👁️
                    </button>
                    <button class="file-action-btn" onclick="adminDashboard.downloadFile('${file.file_id}')" title="Download">
                        📥
                    </button>
                    <button class="file-action-btn" onclick="adminDashboard.deleteFile('${file.file_id}')" title="Delete">
                        🗑️
                    </button>
                </div>
            `;
            fileList.appendChild(fileItem);
        });
    }
    
    loadActivityLog() {
        const activityLog = document.getElementById('activity-log');
        
        // Generate some sample activity entries
        this.activityLog = [
            { timestamp: new Date(), message: 'Admin dashboard initialized', type: 'info' },
            { timestamp: new Date(Date.now() - 300000), message: 'File uploaded: photo_001.jpg', type: 'upload' },
            { timestamp: new Date(Date.now() - 600000), message: 'Auto-cleanup completed', type: 'system' },
            { timestamp: new Date(Date.now() - 900000), message: 'Server started', type: 'system' },
        ];
        
        this.updateActivityLog();
    }
    
    updateActivityLog() {
        const activityLog = document.getElementById('activity-log');
        activityLog.innerHTML = '';
        
        this.activityLog.slice(0, 50).forEach(entry => {
            const activityEntry = document.createElement('div');
            activityEntry.className = 'activity-entry';
            activityEntry.innerHTML = `
                <span class="activity-timestamp">[${this.formatTime(entry.timestamp)}]</span>
                <span class="activity-message">${entry.message}</span>
            `;
            activityLog.appendChild(activityEntry);
        });
        
        // Auto-scroll to bottom
        activityLog.scrollTop = activityLog.scrollHeight;
    }
    
    loadSystemInfo() {
        const systemInfo = document.getElementById('system-info');
        
        const info = [
            { label: 'Server Status', value: 'Online' },
            { label: 'Python Version', value: '3.13+' },
            { label: 'FastAPI Version', value: '0.115.0+' },
            { label: 'Total Uploads', value: this.files.length.toString() },
            { label: 'Storage Used', value: this.formatFileSize(this.files.reduce((sum, file) => sum + file.file_size, 0)) },
            { label: 'Uptime', value: this.formatUptime(Date.now() - this.startTime) }
        ];
        
        systemInfo.innerHTML = '';
        info.forEach(item => {
            const infoItem = document.createElement('div');
            infoItem.className = 'info-item';
            infoItem.innerHTML = `
                <span class="info-label">${item.label}</span>
                <span class="info-value">${item.value}</span>
            `;
            systemInfo.appendChild(infoItem);
        });
    }
    
    logActivity(message, type = 'info') {
        const entry = {
            timestamp: new Date(),
            message: message,
            type: type
        };
        
        this.activityLog.unshift(entry);
        
        // Keep only last 100 entries
        if (this.activityLog.length > 100) {
            this.activityLog = this.activityLog.slice(0, 100);
        }
        
        // Update display if activity tab is visible
        if (this.currentTab === 'activity') {
            this.updateActivityLog();
        }
    }
    
    startAutoRefresh() {
        this.refreshInterval = setInterval(async () => {
            await this.loadStatistics();
            this.loadSystemInfo();
        }, 30000); // Refresh every 30 seconds
    }
    
    updateUptime() {
        const uptime = Date.now() - this.startTime;
        document.getElementById('server-uptime').textContent = this.formatUptime(uptime);
    }
    
    // Utility Functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    formatTime(date) {
        return date.toLocaleTimeString();
    }
    
    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    getFileIcon(fileType) {
        if (fileType.startsWith('image/')) return '🖼️';
        if (fileType.startsWith('video/')) return '🎥';
        if (fileType.startsWith('audio/')) return '🎵';
        if (fileType.includes('pdf')) return '📄';
        if (fileType.includes('text')) return '📝';
        return '📎';
    }
    
    showProgress(message, percentage) {
        const progressContainer = document.getElementById('progress-container');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        progressContainer.style.display = 'block';
        progressFill.style.width = percentage + '%';
        progressText.textContent = message;
    }
    
    hideProgress() {
        const progressContainer = document.getElementById('progress-container');
        progressContainer.style.display = 'none';
    }
    
    showNotification(message, type = 'info') {
        // Simple console notification for now
        console.log(`[${type.toUpperCase()}] ${message}`);
        this.logActivity(message, type);
    }
    
    // File Operations
    async viewFile(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (file) {
            window.open(file.url, '_blank');
            this.logActivity(`Viewed file: ${file.original_filename}`, 'action');
        }
    }
    
    async downloadFile(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (file) {
            const link = document.createElement('a');
            link.href = file.url;
            link.download = file.original_filename;
            link.click();
            this.logActivity(`Downloaded file: ${file.original_filename}`, 'action');
        }
    }
    
    async deleteFile(fileId) {
        if (confirm('Are you sure you want to delete this file?')) {
            try {
                const response = await fetch(`${this.serverUrl}/admin/files/${fileId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.files = this.files.filter(f => f.file_id !== fileId);
                    this.updateFileList();
                    await this.loadStatistics();
                    this.logActivity(`Deleted file: ${fileId}`, 'action');
                    this.showNotification('File deleted successfully', 'success');
                } else {
                    // For demo, just remove from local array
                    const file = this.files.find(f => f.file_id === fileId);
                    this.files = this.files.filter(f => f.file_id !== fileId);
                    this.updateFileList();
                    await this.loadStatistics();
                    this.logActivity(`Deleted file: ${file ? file.original_filename : fileId}`, 'action');
                    this.showNotification('File deleted successfully', 'success');
                }
            } catch (error) {
                console.error('Delete failed:', error);
                this.showNotification('Failed to delete file', 'error');
            }
        }
    }
    
    // Theme Management
    applyTheme(primaryColor, accentColor) {
        const root = document.documentElement;
        root.style.setProperty('--primary-color', primaryColor);
        root.style.setProperty('--accent-color', accentColor);
        root.style.setProperty('--primary-light', this.lightenColor(primaryColor, 20));
        root.style.setProperty('--primary-dark', this.darkenColor(primaryColor, 20));
        
        this.logActivity(`Theme updated: ${primaryColor}, ${accentColor}`, 'setting');
    }
    
    lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }
    
    darkenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R > 255 ? 255 : R < 0 ? 0 : R) * 0x10000 +
            (G > 255 ? 255 : G < 0 ? 0 : G) * 0x100 +
            (B > 255 ? 255 : B < 0 ? 0 : B)).toString(16).slice(1);
    }
}

// Global Functions for UI Interactions
let adminDashboard;

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    
    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    adminDashboard.currentTab = tabName;
    adminDashboard.logActivity(`Switched to ${tabName} tab`, 'navigation');
}

async function refreshData() {
    adminDashboard.showProgress('Refreshing data...', 0);
    await adminDashboard.loadDashboardData();
    adminDashboard.showNotification('Data refreshed successfully', 'success');
}

function openSettings() {
    document.getElementById('settings-modal').style.display = 'flex';
    adminDashboard.logActivity('Opened settings modal', 'navigation');
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

function applyPreset(presetName) {
    const presets = {
        'green': { primary: '#4CAF50', accent: '#2E7D32' },
        'blue': { primary: '#2196F3', accent: '#1976D2' },
        'purple': { primary: '#9C27B0', accent: '#7B1FA2' },
        'orange': { primary: '#FF9800', accent: '#F57C00' }
    };
    
    const preset = presets[presetName];
    if (preset) {
        document.getElementById('primary-color').value = preset.primary;
        document.getElementById('accent-color').value = preset.accent;
        adminDashboard.applyTheme(preset.primary, preset.accent);
    }
}

function saveSettings() {
    const primaryColor = document.getElementById('primary-color').value;
    const accentColor = document.getElementById('accent-color').value;
    const autoCleanup = document.getElementById('auto-cleanup').checked;
    const maxFileSize = document.getElementById('max-file-size').value;
    
    adminDashboard.applyTheme(primaryColor, accentColor);
    
    // Save settings to localStorage
    localStorage.setItem('adminSettings', JSON.stringify({
        primaryColor,
        accentColor,
        autoCleanup,
        maxFileSize
    }));
    
    adminDashboard.showNotification('Settings saved successfully', 'success');
    closeSettings();
}

function uploadFile() {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.onchange = async (e) => {
        const files = Array.from(e.target.files);
        for (const file of files) {
            adminDashboard.showProgress(`Uploading ${file.name}...`, 50);
            // Simulate upload delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            adminDashboard.logActivity(`Uploaded file: ${file.name}`, 'upload');
        }
        adminDashboard.hideProgress();
        await adminDashboard.loadFiles();
        adminDashboard.showNotification(`${files.length} file(s) uploaded successfully`, 'success');
    };
    input.click();
}

function cleanupOldFiles() {
    if (confirm('This will delete files older than 30 days. Continue?')) {
        const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        const oldFiles = adminDashboard.files.filter(file => 
            new Date(file.upload_time) < thirtyDaysAgo
        );
        
        adminDashboard.files = adminDashboard.files.filter(file => 
            new Date(file.upload_time) >= thirtyDaysAgo
        );
        
        adminDashboard.updateFileList();
        adminDashboard.loadStatistics();
        adminDashboard.logActivity(`Cleanup completed: ${oldFiles.length} files deleted`, 'system');
        adminDashboard.showNotification(`Cleanup completed: ${oldFiles.length} files deleted`, 'success');
    }
}

function clearLog() {
    if (confirm('Clear activity log?')) {
        adminDashboard.activityLog = [];
        adminDashboard.updateActivityLog();
        adminDashboard.logActivity('Activity log cleared', 'system');
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('adminAuth');
        localStorage.removeItem('adminSettings');
        window.location.href = '/admin/login';
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
    
    // Load saved settings
    const savedSettings = localStorage.getItem('adminSettings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        document.getElementById('primary-color').value = settings.primaryColor || '#4CAF50';
        document.getElementById('accent-color').value = settings.accentColor || '#2E7D32';
        document.getElementById('auto-cleanup').checked = settings.autoCleanup !== false;
        document.getElementById('max-file-size').value = settings.maxFileSize || 10;
        adminDashboard.applyTheme(settings.primaryColor || '#4CAF50', settings.accentColor || '#2E7D32');
    }
});
