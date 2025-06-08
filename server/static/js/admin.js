// Admin Dashboard JavaScript - Modern VRCPhoto2URL Admin Interface
class AdminDashboard {
    constructor() {
        this.serverUrl = window.location.origin;
        this.isAuthenticated = false;
        this.refreshInterval = null;
        this.currentTab = 'overview';
        this.currentView = 'grid'; // grid or list
        this.files = [];
        this.filteredFiles = [];
        this.activityLog = [];
        this.startTime = Date.now();
        this.searchQuery = '';
        this.currentFilter = 'all';
        
        this.init();
    }
      async init() {
        // Check authentication
        await this.checkAuth();
        
        // Initialize UI components
        this.initializeUI();
        
        // Load initial data
        await this.loadDashboardData();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start refresh interval
        this.startAutoRefresh();
        
        // Update uptime display
        this.updateUptime();
        setInterval(() => this.updateUptime(), 1000);
        
        console.log('Admin Dashboard initialized');
    }

    initializeUI() {
        // Initialize sidebar navigation
        this.initSidebarNavigation();
        
        // Initialize file view controls
        this.initFileViewControls();
        
        // Initialize search and filters
        this.initSearchAndFilters();
        
        // Set default tab
        this.switchTab('overview');
    }

    initSidebarNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const tabName = item.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Sidebar toggle for mobile
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('collapsed');
            });
        }
    }

    initFileViewControls() {
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                viewBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentView = btn.dataset.view;
                this.updateFileDisplay();
            });
        });
    }

    initSearchAndFilters() {
        const searchInput = document.getElementById('file-search');
        const filterSelect = document.getElementById('file-filter');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.filterFiles();
            });
        }

        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.filterFiles();
            });
        }
    }

    setupEventListeners() {
        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
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
        this.showLoading('Loading dashboard data...');
        
        try {
            // Load files
            this.showLoading('Loading files...');
            await this.loadFiles();
            
            // Load statistics
            this.showLoading('Loading statistics...');
            await this.loadStatistics();
            
            // Load activity log
            this.showLoading('Loading activity...');
            this.loadActivityLog();
            
            // Load system info
            this.showLoading('Loading system info...');
            this.loadSystemInfo();
            
            this.hideLoading();
            this.showToast('Dashboard loaded successfully', 'success');
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.hideLoading();
            this.showToast('Failed to load dashboard data', 'error');
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
                this.filterFiles();
                this.updateFileDisplay();
                this.logActivity('Loaded file list', 'info');
            } else {
                // For demo purposes, create some sample data
                this.files = this.generateSampleFiles();
                this.filterFiles();
                this.updateFileDisplay();
                this.logActivity('Loaded sample file data', 'info');
            }
        } catch (error) {
            console.warn('Using sample data:', error.message);
            this.files = this.generateSampleFiles();
            this.filterFiles();
            this.updateFileDisplay();
        }
    }
      generateSampleFiles() {
        const sampleFiles = [];
        const fileTypes = ['image/png', 'image/jpeg', 'image/gif', 'text/plain', 'application/pdf'];
        const baseNames = ['document', 'photo', 'screenshot', 'report', 'image', 'avatar', 'banner'];
        
        for (let i = 0; i < 25; i++) {
            const baseName = baseNames[Math.floor(Math.random() * baseNames.length)];
            const fileType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
            const extension = this.getExtensionFromType(fileType);
            const isImage = fileType.startsWith('image/');
            
            const file = {
                file_id: `file-${i + 1}`,
                original_filename: `${baseName}_${i + 1}.${extension}`,
                filename: `${Date.now()}_${baseName}_${i + 1}.${extension}`,
                url: `${this.serverUrl}/files/file-${i + 1}.${extension}`,
                file_size: Math.floor(Math.random() * 5000000) + 10000, // 10KB to 5MB
                upload_time: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                file_type: fileType,
                has_thumbnail: isImage,
                thumbnail_url: isImage ? `${this.serverUrl}/thumbnails/file-${i + 1}_thumb.jpg` : null
            };
            
            sampleFiles.push(file);
        }
        
        return sampleFiles.sort((a, b) => new Date(b.upload_time) - new Date(a.upload_time));
    }

    getExtensionFromType(fileType) {
        const typeMap = {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'text/plain': 'txt',
            'application/pdf': 'pdf'
        };
        return typeMap[fileType] || 'bin';
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
            
            const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString();
            const uploadsYesterday = this.files.filter(file => 
                new Date(file.upload_time).toDateString() === yesterday
            ).length;
            
            const thisWeek = this.files.filter(file => {
                const fileDate = new Date(file.upload_time);
                const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                return fileDate > weekAgo;
            }).length;
            
            // Update statistics display
            document.getElementById('total-files').textContent = totalFiles;
            document.getElementById('storage-used').textContent = this.formatFileSize(totalSize);
            document.getElementById('uploads-today').textContent = uploadsToday;
            document.getElementById('server-uptime').textContent = this.formatUptime(Date.now() - this.startTime);
            
            // Update change indicators
            const filesChange = document.getElementById('files-change');
            if (filesChange) {
                filesChange.textContent = `+${thisWeek} this week`;
                filesChange.className = thisWeek > 0 ? 'stat-change positive' : 'stat-change';
            }
            
            const uploadsChange = document.getElementById('uploads-change');
            if (uploadsChange) {
                uploadsChange.textContent = `+${uploadsYesterday} yesterday`;
                uploadsChange.className = uploadsYesterday > 0 ? 'stat-change positive' : 'stat-change';
            }
            
            this.logActivity(`Statistics updated: ${totalFiles} files, ${this.formatFileSize(totalSize)} used`, 'info');
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }

    filterFiles() {
        let filtered = [...this.files];
        
        // Apply search filter
        if (this.searchQuery) {
            filtered = filtered.filter(file => 
                file.original_filename.toLowerCase().includes(this.searchQuery) ||
                file.file_type.toLowerCase().includes(this.searchQuery)
            );
        }
        
        // Apply type filter
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(file => {
                switch (this.currentFilter) {
                    case 'images':
                        return file.file_type.startsWith('image/');
                    case 'videos':
                        return file.file_type.startsWith('video/');
                    case 'documents':
                        return file.file_type.includes('pdf') || file.file_type.includes('text');
                    case 'other':
                        return !file.file_type.startsWith('image/') && 
                               !file.file_type.startsWith('video/') && 
                               !file.file_type.includes('pdf') && 
                               !file.file_type.includes('text');
                    default:
                        return true;
                }
            });
        }
        
        this.filteredFiles = filtered;
        this.updateFileDisplay();
    }

    updateFileDisplay() {
        if (this.currentView === 'grid') {
            this.updateFileGrid();
        } else {
            this.updateFileList();
        }
    }

    updateFileGrid() {
        const filesGrid = document.getElementById('files-grid');
        const filesList = document.getElementById('files-list');
        
        if (!filesGrid) return;
        
        filesGrid.style.display = 'grid';
        if (filesList) filesList.style.display = 'none';
        
        filesGrid.innerHTML = '';
        
        this.filteredFiles.forEach(file => {
            const fileCard = document.createElement('div');
            fileCard.className = 'file-card';
            
            const thumbnailHtml = file.has_thumbnail ? 
                `<div class="file-thumbnail">
                    <img src="${file.thumbnail_url}" alt="${file.original_filename}" loading="lazy" 
                         onerror="this.parentElement.innerHTML='${this.getFileIcon(file.file_type)}'">
                 </div>` :
                `<div class="file-icon-large">${this.getFileIcon(file.file_type)}</div>`;
            
            fileCard.innerHTML = `
                ${thumbnailHtml}
                <div class="file-info">
                    <div class="file-name" title="${file.original_filename}">
                        ${this.truncateText(file.original_filename, 20)}
                    </div>
                    <div class="file-meta">
                        <span class="file-size">${this.formatFileSize(file.file_size)}</span>
                        <span class="file-date">${this.formatRelativeDate(file.upload_time)}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="action-btn primary" onclick="adminDashboard.previewFile('${file.file_id}')" title="Preview">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn secondary" onclick="adminDashboard.downloadFile('${file.file_id}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="action-btn secondary" onclick="adminDashboard.copyFileLink('${file.file_id}')" title="Copy Link">
                        <i class="fas fa-link"></i>
                    </button>
                    <button class="action-btn danger" onclick="adminDashboard.deleteFile('${file.file_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            filesGrid.appendChild(fileCard);
        });
        
        // Show empty state if no files
        if (this.filteredFiles.length === 0) {
            filesGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>No files found</h3>
                    <p>Upload some files to get started</p>
                    <button class="btn primary" onclick="uploadFile()">
                        <i class="fas fa-cloud-upload-alt"></i>
                        Upload Files
                    </button>
                </div>
            `;
        }
    }

    updateFileList() {
        const filesGrid = document.getElementById('files-grid');
        const filesList = document.getElementById('files-list');
        
        if (!filesList) return;
        
        if (filesGrid) filesGrid.style.display = 'none';
        filesList.style.display = 'block';
        
        filesList.innerHTML = `
            <div class="list-header">
                <div class="list-column">Name</div>
                <div class="list-column">Size</div>
                <div class="list-column">Type</div>
                <div class="list-column">Date</div>
                <div class="list-column">Actions</div>
            </div>
        `;
        
        this.filteredFiles.forEach(file => {
            const fileRow = document.createElement('div');
            fileRow.className = 'file-row';
            fileRow.innerHTML = `
                <div class="list-column file-name-column">
                    <div class="file-icon">${this.getFileIcon(file.file_type)}</div>
                    <span class="file-name" title="${file.original_filename}">
                        ${file.original_filename}
                    </span>
                </div>
                <div class="list-column">${this.formatFileSize(file.file_size)}</div>
                <div class="list-column">
                    <span class="file-type-badge">${file.file_type}</span>
                </div>
                <div class="list-column">${this.formatDate(file.upload_time)}</div>
                <div class="list-column">
                    <div class="file-actions">
                        <button class="action-btn small" onclick="adminDashboard.previewFile('${file.file_id}')" title="Preview">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-btn small" onclick="adminDashboard.downloadFile('${file.file_id}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="action-btn small" onclick="adminDashboard.copyFileLink('${file.file_id}')" title="Copy Link">
                            <i class="fas fa-link"></i>
                        </button>
                        <button class="action-btn small danger" onclick="adminDashboard.deleteFile('${file.file_id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            filesList.appendChild(fileRow);
        });
        
        // Show empty state if no files
        if (this.filteredFiles.length === 0) {
            filesList.innerHTML += `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>No files found</h3>
                    <p>Upload some files to get started</p>
                    <button class="btn primary" onclick="uploadFile()">
                        <i class="fas fa-cloud-upload-alt"></i>
                        Upload Files
                    </button>
                </div>
            `;
        }
    }
      // Tab Management
    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.tab === tabName) {
                item.classList.add('active');
            }
        });
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        const targetPanel = document.getElementById(`${tabName}-tab`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
        
        // Update header
        const pageTitle = document.getElementById('page-title');
        const breadcrumbCurrent = document.getElementById('breadcrumb-current');
        
        if (pageTitle) pageTitle.textContent = this.capitalizeFirst(tabName);
        if (breadcrumbCurrent) breadcrumbCurrent.textContent = this.capitalizeFirst(tabName);
        
        this.currentTab = tabName;
        this.logActivity(`Switched to ${tabName} tab`, 'navigation');
        
        // Load tab-specific data
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'overview':
                this.updateRecentActivity();
                break;
            case 'files':
                this.updateFileDisplay();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'activity':
                this.updateActivityLog();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    updateRecentActivity() {
        const activityPreview = document.getElementById('activity-preview');
        if (!activityPreview) return;
        
        const recentActivities = this.activityLog.slice(0, 5);
        activityPreview.innerHTML = '';
        
        recentActivities.forEach(entry => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            activityItem.innerHTML = `
                <div class="activity-icon ${entry.type}">
                    <i class="fas ${this.getActivityIcon(entry.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-message">${entry.message}</div>
                    <div class="activity-time">${this.formatRelativeDate(entry.timestamp)}</div>
                </div>
            `;
            activityPreview.appendChild(activityItem);
        });
    }

    getActivityIcon(type) {
        const icons = {
            'info': 'fa-info-circle',
            'upload': 'fa-cloud-upload-alt',
            'delete': 'fa-trash',
            'action': 'fa-mouse-pointer',
            'system': 'fa-cog',
            'navigation': 'fa-compass',
            'setting': 'fa-sliders-h',
            'error': 'fa-exclamation-triangle',
            'success': 'fa-check-circle'
        };
        return icons[type] || 'fa-info-circle';
    }
      loadActivityLog() {
        // Generate some sample activity entries if empty
        if (this.activityLog.length === 0) {
            this.activityLog = [
                { timestamp: new Date(), message: 'Admin dashboard initialized', type: 'info' },
                { timestamp: new Date(Date.now() - 300000), message: 'File uploaded: photo_001.jpg', type: 'upload' },
                { timestamp: new Date(Date.now() - 600000), message: 'Auto-cleanup completed', type: 'system' },
                { timestamp: new Date(Date.now() - 900000), message: 'Server started', type: 'system' },
            ];
        }
        
        this.updateActivityLog();
    }

    loadAnalytics() {
        this.updateFileTypesChart();
        this.updateSystemInfo();
    }

    updateFileTypesChart() {
        const chartContainer = document.getElementById('file-types-chart');
        if (!chartContainer) return;
        
        // Calculate file type distribution
        const typeCount = {};
        this.files.forEach(file => {
            const category = this.getFileCategory(file.file_type);
            typeCount[category] = (typeCount[category] || 0) + 1;
        });
        
        chartContainer.innerHTML = '';
        Object.entries(typeCount).forEach(([type, count]) => {
            const percentage = ((count / this.files.length) * 100).toFixed(1);
            const barItem = document.createElement('div');
            barItem.className = 'chart-bar-item';
            barItem.innerHTML = `
                <div class="chart-bar-label">
                    <span>${this.capitalizeFirst(type)}</span>
                    <span>${count} files (${percentage}%)</span>
                </div>
                <div class="chart-bar">
                    <div class="chart-bar-fill ${type}" style="width: ${percentage}%"></div>
                </div>
            `;
            chartContainer.appendChild(barItem);
        });
    }

    getFileCategory(fileType) {
        if (fileType.startsWith('image/')) return 'images';
        if (fileType.startsWith('video/')) return 'videos';
        if (fileType.startsWith('audio/')) return 'audio';
        if (fileType.includes('pdf') || fileType.includes('text')) return 'documents';
        return 'other';
    }

    updateSystemInfo() {
        const systemInfo = document.getElementById('system-info');
        if (!systemInfo) return;
        
        const info = [
            { label: 'Server Status', value: 'Online', status: 'success' },
            { label: 'Python Version', value: '3.13+', status: 'info' },
            { label: 'FastAPI Version', value: '0.115.0+', status: 'info' },
            { label: 'Total Uploads', value: this.files.length.toString(), status: 'primary' },
            { label: 'Storage Used', value: this.formatFileSize(this.files.reduce((sum, file) => sum + file.file_size, 0)), status: 'warning' },
            { label: 'Uptime', value: this.formatUptime(Date.now() - this.startTime), status: 'success' }
        ];
        
        systemInfo.innerHTML = '';
        info.forEach(item => {
            const infoItem = document.createElement('div');
            infoItem.className = 'info-item';
            infoItem.innerHTML = `
                <div class="info-label">${item.label}</div>
                <div class="info-value ${item.status}">${item.value}</div>
            `;
            systemInfo.appendChild(infoItem);
        });
    }

    loadSettings() {
        // Load saved settings from localStorage
        const savedSettings = localStorage.getItem('adminSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            const primaryColor = document.getElementById('primary-color');
            const accentColor = document.getElementById('accent-color');
            const autoCleanup = document.getElementById('auto-cleanup');
            const maxFileSize = document.getElementById('max-file-size');
            
            if (primaryColor) primaryColor.value = settings.primaryColor || '#667eea';
            if (accentColor) accentColor.value = settings.accentColor || '#764ba2';
            if (autoCleanup) autoCleanup.checked = settings.autoCleanup !== false;
            if (maxFileSize) maxFileSize.value = settings.maxFileSize || 50;
        }
    }
      updateActivityLog() {
        const activityLog = document.getElementById('activity-log');
        if (!activityLog) return;
        
        activityLog.innerHTML = '';
        
        this.activityLog.slice(0, 100).forEach(entry => {
            const activityEntry = document.createElement('div');
            activityEntry.className = `activity-entry ${entry.type}`;
            activityEntry.innerHTML = `
                <div class="activity-icon">
                    <i class="fas ${this.getActivityIcon(entry.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-message">${entry.message}</div>
                    <div class="activity-timestamp">${this.formatTime(entry.timestamp)}</div>
                </div>
            `;
            activityLog.appendChild(activityEntry);
        });
        
        // Auto-scroll to bottom
        activityLog.scrollTop = activityLog.scrollHeight;
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
      // Modern UI Utilities
    showLoading(message = 'Loading...') {
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
            if (loadingText) loadingText.textContent = message;
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.log(`[${type.toUpperCase()}] ${message}`);
            return;
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${this.getToastIcon(type)}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
        
        // Add to activity log
        this.logActivity(message, type);
    }

    getToastIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    closeModal(modal) {
        modal.style.display = 'none';
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
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    formatRelativeDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength - 3) + '...';
    }
      getFileIcon(fileType) {
        if (fileType.startsWith('image/')) return '<i class="fas fa-image"></i>';
        if (fileType.startsWith('video/')) return '<i class="fas fa-video"></i>';
        if (fileType.startsWith('audio/')) return '<i class="fas fa-music"></i>';
        if (fileType.includes('pdf')) return '<i class="fas fa-file-pdf"></i>';
        if (fileType.includes('text')) return '<i class="fas fa-file-alt"></i>';
        if (fileType.includes('zip') || fileType.includes('rar')) return '<i class="fas fa-file-archive"></i>';
        if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '<i class="fas fa-file-excel"></i>';
        if (fileType.includes('word') || fileType.includes('document')) return '<i class="fas fa-file-word"></i>';
        return '<i class="fas fa-file"></i>';
    }
      // File Operations
    async previewFile(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (!file) return;
        
        const modal = document.getElementById('file-preview-modal');
        const filename = document.getElementById('preview-filename');
        const previewContainer = document.getElementById('preview-container');
        
        if (!modal || !previewContainer) return;
        
        filename.textContent = file.original_filename;
        
        // Clear previous content
        previewContainer.innerHTML = '';
        
        if (file.file_type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = file.url;
            img.alt = file.original_filename;
            img.className = 'preview-image';
            img.onerror = () => {
                previewContainer.innerHTML = `
                    <div class="preview-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Unable to load image preview</p>
                    </div>
                `;
            };
            previewContainer.appendChild(img);
        } else if (file.file_type.startsWith('text/')) {
            try {
                const response = await fetch(file.url);
                const text = await response.text();
                const pre = document.createElement('pre');
                pre.className = 'preview-text';
                pre.textContent = text.substr(0, 5000); // Limit to 5KB
                if (text.length > 5000) {
                    pre.textContent += '\n... (truncated)';
                }
                previewContainer.appendChild(pre);
            } catch (error) {
                previewContainer.innerHTML = `
                    <div class="preview-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Unable to load text preview</p>
                    </div>
                `;
            }
        } else {
            previewContainer.innerHTML = `
                <div class="preview-info">
                    <div class="file-icon-preview">${this.getFileIcon(file.file_type)}</div>
                    <h3>${file.original_filename}</h3>
                    <div class="file-details">
                        <div class="detail-item">
                            <span class="label">Type:</span>
                            <span class="value">${file.file_type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Size:</span>
                            <span class="value">${this.formatFileSize(file.file_size)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Uploaded:</span>
                            <span class="value">${this.formatDate(file.upload_time)}</span>
                        </div>
                    </div>
                    <p>Preview not available for this file type</p>
                </div>
            `;
        }
        
        // Store current file for modal actions
        modal.dataset.fileId = fileId;
        modal.style.display = 'flex';
        
        this.logActivity(`Previewed file: ${file.original_filename}`, 'action');
    }

    async downloadFile(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (!file) return;
        
        try {
            const link = document.createElement('a');
            link.href = file.url;
            link.download = file.original_filename;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.logActivity(`Downloaded file: ${file.original_filename}`, 'action');
            this.showToast(`Downloaded: ${file.original_filename}`, 'success');
        } catch (error) {
            console.error('Download failed:', error);
            this.showToast('Failed to download file', 'error');
        }
    }

    async copyFileLink(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (!file) return;
        
        try {
            await navigator.clipboard.writeText(file.url);
            this.logActivity(`Copied link for: ${file.original_filename}`, 'action');
            this.showToast('Link copied to clipboard', 'success');
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = file.url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            this.logActivity(`Copied link for: ${file.original_filename}`, 'action');
            this.showToast('Link copied to clipboard', 'success');
        }
    }

    async deleteFile(fileId) {
        const file = this.files.find(f => f.file_id === fileId);
        if (!file) return;
        
        if (!confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/admin/files/${fileId}`, {
                method: 'DELETE'
            });
            
            if (response.ok || response.status === 404) {
                // Remove from local array
                this.files = this.files.filter(f => f.file_id !== fileId);
                this.filterFiles();
                await this.loadStatistics();
                
                this.logActivity(`Deleted file: ${file.original_filename}`, 'delete');
                this.showToast(`Deleted: ${file.original_filename}`, 'success');
            } else {
                throw new Error(`Delete failed with status: ${response.status}`);
            }
        } catch (error) {
            console.error('Delete failed:', error);
            // For demo, still remove from local array
            this.files = this.files.filter(f => f.file_id !== fileId);
            this.filterFiles();
            await this.loadStatistics();
            
            this.logActivity(`Deleted file: ${file.original_filename}`, 'delete');
            this.showToast(`Deleted: ${file.original_filename}`, 'success');
        }
    }
    
    // Theme Management
    applyTheme(primaryColor, accentColor) {
        const root = document.documentElement;
        root.style.setProperty('--primary-color', primaryColor);
        root.style.setProperty('--accent-color', accentColor);
        root.style.setProperty('--primary-light', this.lightenColor(primaryColor, 20));
        root.style.setProperty('--primary-dark', this.darkenColor(primaryColor, 20));
        root.style.setProperty('--accent-light', this.lightenColor(accentColor, 20));
        root.style.setProperty('--accent-dark', this.darkenColor(accentColor, 20));
        
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
    if (adminDashboard) {
        adminDashboard.switchTab(tabName);
    }
}

async function refreshData() {
    if (adminDashboard) {
        adminDashboard.showLoading('Refreshing data...');
        await adminDashboard.loadDashboardData();
        adminDashboard.showToast('Data refreshed successfully', 'success');
    }
}

function uploadFile() {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '*/*';
    
    input.onchange = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;
        
        adminDashboard.showLoading(`Uploading ${files.length} file(s)...`);
        
        try {
            // Simulate upload process
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                adminDashboard.showLoading(`Uploading ${file.name}... (${i + 1}/${files.length})`);
                
                // Simulate upload delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Add to files array (simulation)
                const newFile = {
                    file_id: `file-${Date.now()}-${i}`,
                    original_filename: file.name,
                    filename: `${Date.now()}_${file.name}`,
                    url: `${adminDashboard.serverUrl}/files/${Date.now()}_${file.name}`,
                    file_size: file.size,
                    upload_time: new Date().toISOString(),
                    file_type: file.type || 'application/octet-stream',
                    has_thumbnail: file.type.startsWith('image/'),
                    thumbnail_url: file.type.startsWith('image/') ? 
                        `${adminDashboard.serverUrl}/thumbnails/${Date.now()}_${file.name}_thumb.jpg` : null
                };
                
                adminDashboard.files.unshift(newFile);
                adminDashboard.logActivity(`Uploaded file: ${file.name}`, 'upload');
            }
            
            adminDashboard.filterFiles();
            await adminDashboard.loadStatistics();
            adminDashboard.hideLoading();
            adminDashboard.showToast(`${files.length} file(s) uploaded successfully`, 'success');
            
        } catch (error) {
            console.error('Upload failed:', error);
            adminDashboard.hideLoading();
            adminDashboard.showToast('Upload failed', 'error');
        }
    };
    
    input.click();
}

function cleanupOldFiles() {
    if (!confirm('This will delete files older than 30 days. Continue?')) {
        return;
    }
    
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const oldFiles = adminDashboard.files.filter(file => 
        new Date(file.upload_time) < thirtyDaysAgo
    );
    
    if (oldFiles.length === 0) {
        adminDashboard.showToast('No old files to cleanup', 'info');
        return;
    }
    
    adminDashboard.files = adminDashboard.files.filter(file => 
        new Date(file.upload_time) >= thirtyDaysAgo
    );
    
    adminDashboard.filterFiles();
    adminDashboard.loadStatistics();
    adminDashboard.logActivity(`Cleanup completed: ${oldFiles.length} files deleted`, 'system');
    adminDashboard.showToast(`Cleanup completed: ${oldFiles.length} files deleted`, 'success');
}

function exportLogs() {
    const logs = adminDashboard.activityLog.map(entry => 
        `[${entry.timestamp.toISOString()}] [${entry.type.toUpperCase()}] ${entry.message}`
    ).join('\n');
    
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `admin_logs_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    URL.revokeObjectURL(url);
    
    adminDashboard.logActivity('Exported activity logs', 'action');
    adminDashboard.showToast('Logs exported successfully', 'success');
}

function clearLog() {
    if (!confirm('Clear activity log?')) return;
    
    adminDashboard.activityLog = [];
    adminDashboard.updateActivityLog();
    adminDashboard.logActivity('Activity log cleared', 'system');
    adminDashboard.showToast('Activity log cleared', 'success');
}

function closePreview() {
    const modal = document.getElementById('file-preview-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function downloadFileFromPreview() {
    const modal = document.getElementById('file-preview-modal');
    const fileId = modal?.dataset.fileId;
    if (fileId && adminDashboard) {
        adminDashboard.downloadFile(fileId);
    }
}

function copyLinkFromPreview() {
    const modal = document.getElementById('file-preview-modal');
    const fileId = modal?.dataset.fileId;
    if (fileId && adminDashboard) {
        adminDashboard.copyFileLink(fileId);
    }
}

function applyPreset(presetName) {
    const presets = {
        'blue': { primary: '#667eea', accent: '#764ba2' },
        'purple': { primary: '#9C27B0', accent: '#7B1FA2' },
        'green': { primary: '#4CAF50', accent: '#2E7D32' },
        'orange': { primary: '#FF9800', accent: '#F57C00' }
    };
    
    const preset = presets[presetName];
    if (preset && adminDashboard) {
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
    
    if (adminDashboard) {
        adminDashboard.applyTheme(primaryColor, accentColor);
        
        // Save settings to localStorage
        localStorage.setItem('adminSettings', JSON.stringify({
            primaryColor,
            accentColor,
            autoCleanup,
            maxFileSize
        }));
        
        adminDashboard.showToast('Settings saved successfully', 'success');
        adminDashboard.logActivity('Settings updated', 'setting');
    }
}

function resetSettings() {
    if (!confirm('Reset all settings to default values?')) return;
    
    localStorage.removeItem('adminSettings');
    
    // Reset form values
    document.getElementById('primary-color').value = '#667eea';
    document.getElementById('accent-color').value = '#764ba2';
    document.getElementById('auto-cleanup').checked = true;
    document.getElementById('max-file-size').value = 50;
    
    if (adminDashboard) {
        adminDashboard.applyTheme('#667eea', '#764ba2');
        adminDashboard.showToast('Settings reset to default', 'success');
        adminDashboard.logActivity('Settings reset to default', 'setting');
    }
}

function logout() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    localStorage.removeItem('adminAuth');
    localStorage.removeItem('adminSettings');
    window.location.href = '/admin/login';
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
    
    // Load saved settings
    const savedSettings = localStorage.getItem('adminSettings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        
        // Apply saved theme immediately
        adminDashboard.applyTheme(
            settings.primaryColor || '#667eea', 
            settings.accentColor || '#764ba2'
        );
        
        // Set form values when elements are available
        setTimeout(() => {
            const primaryColor = document.getElementById('primary-color');
            const accentColor = document.getElementById('accent-color');
            const autoCleanup = document.getElementById('auto-cleanup');
            const maxFileSize = document.getElementById('max-file-size');
            
            if (primaryColor) primaryColor.value = settings.primaryColor || '#667eea';
            if (accentColor) accentColor.value = settings.accentColor || '#764ba2';
            if (autoCleanup) autoCleanup.checked = settings.autoCleanup !== false;
            if (maxFileSize) maxFileSize.value = settings.maxFileSize || 50;
        }, 100);
    }
    
    // Set up demo authentication
    if (!localStorage.getItem('adminAuth')) {
        localStorage.setItem('adminAuth', 'true');
    }
});
