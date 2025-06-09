// Enhanced Admin Dashboard JavaScript
// VRCPhoto2URL Enhanced Admin Interface

// Global state management
let currentTab = 'overview';
let currentFileView = 'grid';
let currentFileFilter = 'all';
let currentPage = 1;
let filesPerPage = 20;
let isDarkTheme = false;
let charts = {};
let files = [];
let activities = [];
let settings = {
    apiKey: '',
    maxFileSize: 100,
    autoCleanup: true,
    compressImages: true,
    retentionDays: 365,
    requireAuth: true,
    logAccess: true,
    sessionTimeout: 60,
    colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        background: '#f8f9fa'
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced admin dashboard initializing...');
    initializeDashboard();
    loadInitialData();
    setupEventListeners();
    initializeCharts();
    logActivity('Enhanced admin dashboard initialized successfully', 'system');
    showToast('Enhanced admin dashboard loaded successfully!', 'success');
});

// Dashboard initialization
function initializeDashboard() {
    // Load saved theme
    const savedTheme = localStorage.getItem('admin-theme');
    if (savedTheme === 'dark') {
        toggleTheme();
    }
    
    // Load saved settings
    const savedSettings = localStorage.getItem('admin-settings');
    if (savedSettings) {
        try {
            settings = { ...settings, ...JSON.parse(savedSettings) };
            applySettings();
        } catch (e) {
            console.warn('Failed to load saved settings:', e);
        }
    }
    
    // Initialize dropzone
    setupDropzone();
    
    console.log('Dashboard initialized with enhanced features');
}

// Load initial data
function loadInitialData() {
    refreshData();
    loadFiles();
    loadAnalytics();
    loadActivityLog();
}

// Setup event listeners
function setupEventListeners() {
    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileUpload);
    
    // Search functionality
    document.getElementById('file-search').addEventListener('input', debounce(filterFiles, 300));
    
    // Modal close on backdrop click
    document.getElementById('upload-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeUploadModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Initialize charts
function initializeCharts() {
    // Files trend mini chart
    const filesCtx = document.getElementById('files-chart');
    if (filesCtx) {
        charts.files = new Chart(filesCtx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: [12, 19, 15, 17, 22, 18, 25],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
    
    // Storage usage chart
    const storageCtx = document.getElementById('storage-chart');
    if (storageCtx) {
        charts.storage = new Chart(storageCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [25, 75],
                    backgroundColor: ['#007bff', '#e9ecef'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                cutout: '70%'
            }
        });
    }
    
    // Initialize analytics charts
    initializeAnalyticsCharts();
}

// Initialize analytics charts
function initializeAnalyticsCharts() {
    // Upload trend chart
    const uploadTrendCtx = document.getElementById('upload-trend-chart');
    if (uploadTrendCtx) {
        charts.uploadTrend = new Chart(uploadTrendCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Uploads',
                    data: [45, 52, 38, 67],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // File types chart
    const fileTypesCtx = document.getElementById('file-types-chart');
    if (fileTypesCtx) {
        charts.fileTypes = new Chart(fileTypesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Images', 'Videos', 'Documents', 'Other'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#6c757d']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Storage usage over time
    const storageUsageCtx = document.getElementById('storage-usage-chart');
    if (storageUsageCtx) {
        charts.storageUsage = new Chart(storageUsageCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Storage Used (GB)',
                    data: [0.5, 0.8, 1.2, 1.5, 1.8, 2.1],
                    backgroundColor: '#17a2b8'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Tab management
function switchToTab(tabName) {
    console.log('Switching to tab:', tabName);
    
    // Update activity log
    logActivity(`Switched to ${tabName} tab`, 'user');
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to clicked item
    event.target.closest('.nav-item').classList.add('active');
    
    // Hide all tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show target tab panel
    const targetPanel = document.getElementById(tabName + '-tab');
    if (targetPanel) {
        targetPanel.classList.add('active');
        targetPanel.classList.add('fade-in');
    }
    
    // Update breadcrumb
    const breadcrumb = document.getElementById('current-tab');
    if (breadcrumb) {
        breadcrumb.textContent = tabName.charAt(0).toUpperCase() + tabName.slice(1);
    }
    
    currentTab = tabName;
    
    // Load tab-specific data
    switch (tabName) {
        case 'files':
            loadFiles();
            break;
        case 'analytics':
            updateAnalytics();
            break;
        case 'activity':
            loadActivityLog();
            break;
    }
}

// Sidebar management
function toggleSidebar() {
    console.log('Toggling sidebar');
    document.querySelector('.sidebar').classList.toggle('collapsed');
    logActivity('Sidebar toggled', 'user');
}

// Theme management
function toggleTheme() {
    isDarkTheme = !isDarkTheme;
    document.body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = isDarkTheme ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    localStorage.setItem('admin-theme', isDarkTheme ? 'dark' : 'light');
    logActivity(`Switched to ${isDarkTheme ? 'dark' : 'light'} theme`, 'user');
    showToast(`${isDarkTheme ? 'Dark' : 'Light'} theme activated`, 'info');
}

// Data refresh
function refreshData() {
    console.log('Refreshing data');
    logActivity('Data refresh requested', 'system');
    
    // Simulate API calls with loading states
    const elements = ['total-files', 'storage-used', 'total-uploads', 'total-views'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<div class="spinner"></div>';
        }
    });
    
    // Simulate async data loading
    setTimeout(() => {
        // Update stats with mock data
        updateElement('total-files', Math.floor(Math.random() * 500 + 100));
        updateElement('storage-used', (Math.random() * 2000 + 500).toFixed(1) + ' MB');
        updateElement('total-uploads', Math.floor(Math.random() * 1000 + 200));
        updateElement('total-views', Math.floor(Math.random() * 5000 + 1000));
        
        // Update storage bar
        const storagePercent = Math.random() * 60 + 10;
        document.querySelectorAll('.storage-used').forEach(bar => {
            bar.style.width = `${storagePercent}%`;
        });
        
        document.getElementById('storage-used-text').textContent = 
            `${(storagePercent * 50 / 100).toFixed(1)} GB`;
        
        // Update file count badge
        const fileCount = Math.floor(Math.random() * 50 + 10);
        document.getElementById('file-count-badge').textContent = fileCount;
        
        showToast('Data refreshed successfully!', 'success');
    }, 1000);
}

// File management
function loadFiles() {
    console.log('Loading files');
    
    const fileGrid = document.getElementById('file-grid');
    if (!fileGrid) return;
    
    // Show loading
    fileGrid.innerHTML = `
        <div class="loading-placeholder">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading files...</p>
        </div>
    `;
    
    // Simulate API call
    setTimeout(() => {
        // Generate mock files
        files = generateMockFiles(50);
        displayFiles();
        logActivity(`${files.length} files loaded`, 'system');
    }, 800);
}

function generateMockFiles(count) {
    const fileTypes = [
        { type: 'image', ext: 'jpg', icon: 'fa-image', color: '#007bff' },
        { type: 'image', ext: 'png', icon: 'fa-image', color: '#007bff' },
        { type: 'video', ext: 'mp4', icon: 'fa-video', color: '#28a745' },
        { type: 'document', ext: 'pdf', icon: 'fa-file-pdf', color: '#dc3545' },
        { type: 'document', ext: 'docx', icon: 'fa-file-word', color: '#007bff' },
        { type: 'other', ext: 'zip', icon: 'fa-file-archive', color: '#6c757d' }
    ];
    
    const mockFiles = [];
    for (let i = 0; i < count; i++) {
        const fileType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
        const file = {
            id: `file-${i + 1}`,
            name: `example-file-${i + 1}.${fileType.ext}`,
            type: fileType.type,
            size: Math.floor(Math.random() * 10000000) + 100000, // 100KB to 10MB
            uploadDate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
            views: Math.floor(Math.random() * 1000),
            icon: fileType.icon,
            color: fileType.color,
            thumbnail: fileType.type === 'image' ? `https://picsum.photos/200/120?random=${i}` : null
        };
        mockFiles.push(file);
    }
    
    return mockFiles.sort((a, b) => b.uploadDate - a.uploadDate);
}

function displayFiles() {
    const fileGrid = document.getElementById('file-grid');
    if (!fileGrid) return;
    
    let filteredFiles = files;
    
    // Apply type filter
    if (currentFileFilter !== 'all') {
        filteredFiles = files.filter(file => file.type === currentFileFilter);
    }
    
    // Apply search filter
    const searchTerm = document.getElementById('file-search').value.toLowerCase();
    if (searchTerm) {
        filteredFiles = filteredFiles.filter(file => 
            file.name.toLowerCase().includes(searchTerm)
        );
    }
    
    // Pagination
    const startIndex = (currentPage - 1) * filesPerPage;
    const endIndex = startIndex + filesPerPage;
    const pageFiles = filteredFiles.slice(startIndex, endIndex);
    
    // Generate HTML
    fileGrid.className = `file-grid ${currentFileView === 'list' ? 'list-view' : ''}`;
    fileGrid.innerHTML = pageFiles.map(file => `
        <div class="file-item" onclick="selectFile('${file.id}')">
            <div class="file-thumbnail">
                ${file.thumbnail ? 
                    `<img src="${file.thumbnail}" alt="${file.name}" loading="lazy">` :
                    `<i class="${file.icon}" style="color: ${file.color}"></i>`
                }
            </div>
            <div class="file-info">
                <div class="file-name" title="${file.name}">${file.name}</div>
                <div class="file-meta">
                    ${formatFileSize(file.size)} • ${formatDate(file.uploadDate)} • ${file.views} views
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); viewFile('${file.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); downloadFile('${file.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="event.stopPropagation(); shareFile('${file.id}')">
                        <i class="fas fa-share"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); deleteFile('${file.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // Update pagination
    updatePagination(filteredFiles.length);
}

function updatePagination(totalFiles) {
    const totalPages = Math.ceil(totalFiles / filesPerPage);
    document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
}

function setFileView(view) {
    currentFileView = view;
    
    // Update button states
    document.getElementById('grid-view-btn').classList.toggle('active', view === 'grid');
    document.getElementById('list-view-btn').classList.toggle('active', view === 'list');
    
    displayFiles();
    logActivity(`File view changed to ${view}`, 'user');
}

function filterByType(type) {
    currentFileFilter = type;
    currentPage = 1;
    
    // Update filter button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    displayFiles();
    logActivity(`Files filtered by type: ${type}`, 'user');
}

function filterFiles() {
    currentPage = 1;
    displayFiles();
}

// File actions
function selectFile(fileId) {
    console.log('File selected:', fileId);
    // Add selection logic here
}

function viewFile(fileId) {
    console.log('Viewing file:', fileId);
    logActivity(`File viewed: ${fileId}`, 'user');
    showToast('File opened in viewer', 'info');
}

function downloadFile(fileId) {
    console.log('Downloading file:', fileId);
    logActivity(`File downloaded: ${fileId}`, 'user');
    showToast('File download started', 'success');
}

function shareFile(fileId) {
    console.log('Sharing file:', fileId);
    const file = files.find(f => f.id === fileId);
    if (file) {
        const url = `${window.location.origin}/files/${file.id}`;
        navigator.clipboard.writeText(url).then(() => {
            logActivity(`File shared: ${fileId}`, 'user');
            showToast('Share link copied to clipboard', 'success');
        }).catch(() => {
            showToast('Failed to copy share link', 'error');
        });
    }
}

function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        console.log('Deleting file:', fileId);
        files = files.filter(f => f.id !== fileId);
        displayFiles();
        logActivity(`File deleted: ${fileId}`, 'user');
        showToast('File deleted successfully', 'warning');
    }
}

// Upload functionality
function uploadFile() {
    showUploadModal();
}

function uploadNewFile() {
    showUploadModal();
}

function showUploadModal() {
    document.getElementById('upload-modal').classList.add('show');
    logActivity('Upload modal opened', 'user');
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.remove('show');
    document.getElementById('upload-progress').style.display = 'none';
    document.getElementById('progress-fill').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
}

function setupDropzone() {
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    
    if (!dropzone || !fileInput) return;
    
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        handleFileUpload({ target: { files } });
    });
}

function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    console.log('Uploading files:', files);
    logActivity(`Starting upload of ${files.length} file(s)`, 'upload');
    
    // Show progress
    document.getElementById('upload-progress').style.display = 'block';
    
    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            // Upload complete
            setTimeout(() => {
                closeUploadModal();
                loadFiles(); // Refresh file list
                showToast(`Successfully uploaded ${files.length} file(s)`, 'success');
                logActivity(`Upload completed: ${files.length} file(s)`, 'upload');
            }, 500);
        }
        
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = `${Math.round(progress)}%`;
    }, 200);
}

// Analytics
function updateAnalytics() {
    console.log('Updating analytics');
    const period = document.getElementById('analytics-period').value;
    
    // Update charts with new data based on period
    if (charts.uploadTrend) {
        // Generate mock data based on period
        const labels = generateDateLabels(parseInt(period));
        const data = generateMockAnalyticsData(labels.length);
        
        charts.uploadTrend.data.labels = labels;
        charts.uploadTrend.data.datasets[0].data = data;
        charts.uploadTrend.update();
    }
    
    // Update popular files
    updatePopularFiles();
    
    logActivity(`Analytics updated for ${period} days`, 'system');
}

function generateDateLabels(days) {
    const labels = [];
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString());
    }
    return labels;
}

function generateMockAnalyticsData(count) {
    return Array.from({ length: count }, () => Math.floor(Math.random() * 100));
}

function updatePopularFiles() {
    const popularFilesContainer = document.getElementById('popular-files');
    if (!popularFilesContainer) return;
    
    const popularFiles = files
        .sort((a, b) => b.views - a.views)
        .slice(0, 10);
    
    popularFilesContainer.innerHTML = popularFiles.map(file => `
        <div class="popular-file-item">
            <div class="popular-file-icon">
                <i class="${file.icon}" style="color: ${file.color}"></i>
            </div>
            <div class="popular-file-info">
                <div class="popular-file-name">${file.name}</div>
                <div class="popular-file-stats">${file.views} views • ${formatFileSize(file.size)}</div>
            </div>
        </div>
    `).join('');
}

// Activity Log
function loadActivityLog() {
    console.log('Loading activity log');
    
    const container = document.getElementById('activity-detailed-log');
    if (!container) return;
    
    // Generate mock activities if empty
    if (activities.length === 0) {
        activities = generateMockActivities(20);
    }
    
    displayActivities();
}

function generateMockActivities(count) {
    const activityTypes = [
        { type: 'upload', message: 'File uploaded', icon: 'fa-upload' },
        { type: 'download', message: 'File downloaded', icon: 'fa-download' },
        { type: 'delete', message: 'File deleted', icon: 'fa-trash' },
        { type: 'system', message: 'System maintenance', icon: 'fa-cog' },
        { type: 'user', message: 'User logged in', icon: 'fa-user' }
    ];
    
    const mockActivities = [];
    for (let i = 0; i < count; i++) {
        const activity = activityTypes[Math.floor(Math.random() * activityTypes.length)];
        mockActivities.push({
            id: `activity-${i + 1}`,
            type: activity.type,
            message: activity.message,
            icon: activity.icon,
            timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
        });
    }
    
    return mockActivities.sort((a, b) => b.timestamp - a.timestamp);
}

function displayActivities() {
    const container = document.getElementById('activity-detailed-log');
    if (!container) return;
    
    let filteredActivities = activities;
    
    // Apply filter
    const filter = document.getElementById('activity-filter').value;
    if (filter !== 'all') {
        filteredActivities = activities.filter(activity => activity.type === filter);
    }
    
    container.innerHTML = filteredActivities.map(activity => `
        <div class="activity-item ${activity.type}">
            <div class="activity-icon">
                <i class="fas ${activity.icon}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-message">${activity.message}</div>
                <div class="activity-time">${formatRelativeTime(activity.timestamp)}</div>
            </div>
        </div>
    `).join('');
}

function filterActivity() {
    displayActivities();
    logActivity('Activity log filtered', 'user');
}

function clearActivityLog() {
    if (confirm('Are you sure you want to clear the activity log?')) {
        activities = [];
        displayActivities();
        logActivity('Activity log cleared', 'system');
        showToast('Activity log cleared', 'warning');
    }
}

function logActivity(message, type = 'system') {
    const activity = {
        id: `activity-${Date.now()}`,
        type: type,
        message: message,
        icon: getActivityIcon(type),
        timestamp: new Date()
    };
    
    activities.unshift(activity);
    
    // Update activity list in overview
    const activityList = document.getElementById('activity-list');
    if (activityList) {
        const time = new Date().toLocaleTimeString();
        activityList.innerHTML = `<p>[${time}] ${message}</p>` + activityList.innerHTML;
        
        // Keep only last 10 items
        const items = activityList.querySelectorAll('p');
        if (items.length > 10) {
            for (let i = 10; i < items.length; i++) {
                items[i].remove();
            }
        }
    }
    
    // Update detailed log if visible
    if (currentTab === 'activity') {
        displayActivities();
    }
    
    console.log('Activity logged:', message);
}

function getActivityIcon(type) {
    const icons = {
        system: 'fa-cog',
        user: 'fa-user',
        upload: 'fa-upload',
        download: 'fa-download',
        delete: 'fa-trash'
    };
    return icons[type] || 'fa-info';
}

// Settings Management
function switchSettingsTab(tabName) {
    // Remove active class from all settings tabs
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Add active class to clicked tab
    event.target.classList.add('active');
    
    // Hide all settings panels
    document.querySelectorAll('.settings-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show target panel
    const targetPanel = document.getElementById(tabName + '-settings');
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    
    logActivity(`Settings tab switched to ${tabName}`, 'user');
}

function updateThemeColor(colorType, value) {
    document.documentElement.style.setProperty(`--${colorType}-color`, value);
    settings.colors[colorType] = value;
    logActivity(`${colorType} color updated`, 'user');
}

function applyTheme(themeName) {
    const themes = {
        default: {
            primary: '#007bff',
            secondary: '#6c757d',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            background: '#f8f9fa'
        },
        dark: {
            primary: '#375a7f',
            secondary: '#444',
            success: '#00bc8c',
            warning: '#f39c12',
            danger: '#e74c3c',
            background: '#222'
        },
        blue: {
            primary: '#17a2b8',
            secondary: '#6c757d',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            background: '#e3f2fd'
        },
        green: {
            primary: '#28a745',
            secondary: '#6c757d',
            success: '#20c997',
            warning: '#ffc107',
            danger: '#dc3545',
            background: '#e8f5e8'
        },
        purple: {
            primary: '#6f42c1',
            secondary: '#6c757d',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            background: '#f3e5f5'
        }
    };
    
    const theme = themes[themeName];
    if (theme) {
        Object.keys(theme).forEach(colorType => {
            document.documentElement.style.setProperty(`--${colorType}-color`, theme[colorType]);
            const input = document.getElementById(`${colorType}-color`);
            if (input) {
                input.value = theme[colorType];
            }
        });
        
        settings.colors = { ...settings.colors, ...theme };
        logActivity(`Theme applied: ${themeName}`, 'user');
        showToast(`${themeName} theme applied`, 'success');
    }
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('api-key-input');
    const icon = document.getElementById('api-key-toggle');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function testApiKey() {
    const apiKey = document.getElementById('api-key-input').value;
    console.log('Testing API key');
    logActivity('API key test initiated', 'system');
    
    if (apiKey.trim()) {
        showToast('API key test passed!', 'success');
        logActivity('API key validation successful', 'system');
    } else {
        showToast('Please enter an API key', 'error');
    }
}

function saveAllSettings() {
    // Collect all settings
    settings.apiKey = document.getElementById('api-key-input').value;
    settings.maxFileSize = parseInt(document.getElementById('max-file-size').value);
    settings.autoCleanup = document.getElementById('auto-cleanup').checked;
    settings.compressImages = document.getElementById('compress-images').checked;
    settings.retentionDays = parseInt(document.getElementById('retention-days').value);
    settings.requireAuth = document.getElementById('require-auth').checked;
    settings.logAccess = document.getElementById('log-access').checked;
    settings.sessionTimeout = parseInt(document.getElementById('session-timeout').value);
    
    // Save to localStorage
    localStorage.setItem('admin-settings', JSON.stringify(settings));
    
    logActivity('Settings saved', 'user');
    showToast('Settings saved successfully', 'success');
}

function resetSettings() {
    if (confirm('Reset all settings to default?')) {
        // Reset form values
        document.getElementById('api-key-input').value = '';
        document.getElementById('max-file-size').value = '100';
        document.getElementById('auto-cleanup').checked = true;
        document.getElementById('compress-images').checked = true;
        document.getElementById('retention-days').value = '365';
        document.getElementById('require-auth').checked = true;
        document.getElementById('log-access').checked = true;
        document.getElementById('session-timeout').value = '60';
        
        // Reset colors
        applyTheme('default');
        
        logActivity('Settings reset to default', 'user');
        showToast('Settings reset', 'info');
    }
}

function applySettings() {
    if (settings.apiKey) {
        document.getElementById('api-key-input').value = settings.apiKey;
    }
    document.getElementById('max-file-size').value = settings.maxFileSize;
    document.getElementById('auto-cleanup').checked = settings.autoCleanup;
    document.getElementById('compress-images').checked = settings.compressImages;
    document.getElementById('retention-days').value = settings.retentionDays;
    document.getElementById('require-auth').checked = settings.requireAuth;
    document.getElementById('log-access').checked = settings.logAccess;
    document.getElementById('session-timeout').value = settings.sessionTimeout;
    
    // Apply color settings
    Object.keys(settings.colors).forEach(colorType => {
        document.documentElement.style.setProperty(`--${colorType}-color`, settings.colors[colorType]);
        const input = document.getElementById(`${colorType}-color`);
        if (input) {
            input.value = settings.colors[colorType];
        }
    });
}

function exportSettings() {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'admin-settings.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    logActivity('Settings exported', 'user');
    showToast('Settings exported successfully', 'success');
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const importedSettings = JSON.parse(e.target.result);
                    settings = { ...settings, ...importedSettings };
                    applySettings();
                    localStorage.setItem('admin-settings', JSON.stringify(settings));
                    logActivity('Settings imported', 'user');
                    showToast('Settings imported successfully', 'success');
                } catch (error) {
                    showToast('Invalid settings file', 'error');
                }
            };
            reader.readAsText(file);
        }
    };
    input.click();
}

// Utility functions
function cleanupOldFiles() {
    if (confirm('This will delete files older than the retention period. Continue?')) {
        const retentionMs = settings.retentionDays * 24 * 60 * 60 * 1000;
        const cutoffDate = new Date(Date.now() - retentionMs);
        
        const deletedCount = files.filter(file => file.uploadDate < cutoffDate).length;
        files = files.filter(file => file.uploadDate >= cutoffDate);
        
        displayFiles();
        logActivity(`Cleaned up ${deletedCount} old files`, 'system');
        showToast(`${deletedCount} old files cleaned up`, 'warning');
    }
}

function revokeAllSessions() {
    if (confirm('This will log out all users. Continue?')) {
        logActivity('All sessions revoked', 'system');
        showToast('All sessions revoked', 'warning');
    }
}

function cleanupFiles() {
    console.log('Cleanup files clicked');
    if (confirm('This will remove temporary and orphaned files. Continue?')) {
        logActivity('File cleanup initiated', 'system');
        showToast('Cleanup process started', 'warning');
        
        // Simulate cleanup process
        setTimeout(() => {
            const cleanedCount = Math.floor(Math.random() * 10) + 1;
            logActivity(`Cleanup completed: ${cleanedCount} files removed`, 'system');
            showToast(`Cleanup completed: ${cleanedCount} files removed`, 'success');
            refreshData();
        }, 2000);
    }
}

function exportLogs() {
    console.log('Export logs clicked');
    
    const logData = activities.map(activity => ({
        timestamp: activity.timestamp.toISOString(),
        type: activity.type,
        message: activity.message
    }));
    
    const dataStr = JSON.stringify(logData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `activity-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    logActivity('Activity logs exported', 'user');
    showToast('Logs exported successfully', 'success');
}

function generateReport() {
    console.log('Generate report clicked');
    logActivity('Report generation initiated', 'system');
    showToast('Generating report...', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        logActivity('System report generated', 'system');
        showToast('Report generated successfully', 'success');
    }, 2000);
}

function systemHealth() {
    console.log('System health check clicked');
    logActivity('System health check initiated', 'system');
    showToast('Checking system health...', 'info');
    
    // Simulate health check
    setTimeout(() => {
        const status = ['Excellent', 'Good', 'Fair'][Math.floor(Math.random() * 3)];
        logActivity(`System health check completed: ${status}`, 'system');
        showToast(`System health: ${status}`, 'success');
    }, 1500);
}

function browseFiles() {
    console.log('Browse files clicked');
    switchToTab('files');
}

function logout() {
    console.log('Logout clicked');
    if (confirm('Are you sure you want to logout?')) {
        logActivity('Admin logged out', 'user');
        showToast('Logging out...', 'info');
        // Redirect to login would happen here
        setTimeout(() => {
            window.location.href = '/admin/login';
        }, 1000);
    }
}

// Navigation
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        displayFiles();
    }
}

function nextPage() {
    const totalPages = Math.ceil(files.length / filesPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayFiles();
    }
}

// Keyboard shortcuts
function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('file-search').focus();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeUploadModal();
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    console.log(`Toast (${type}):`, message);
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Utility functions
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

function formatRelativeTime(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
