// Admin Dashboard JavaScript - Modern VRCPhoto2URL Admin Interface
class AdminDashboard {
    constructor() {
        this.serverUrl = window.location.origin;
        this.apiKey = localStorage.getItem('vrcphoto2url_api_key') || 'your-secret-api-key-change-this';
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
        
        // Performance optimization properties
        this.currentPage = 1;
        this.itemsPerPage = 24; // 6x4 grid
        this.totalPages = 1;
        this.isLoading = false;
        this.loadedThumbnails = new Set();
        
        // Intersection observer for lazy loading
        this.intersectionObserver = null;
        
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
        
        // Initialize window state detection
        this.initWindowStateDetection();
        
        // Start refresh interval
        this.startAutoRefresh();
        
        // Update uptime display
        this.updateUptime();
        setInterval(() => this.updateUptime(), 1000);
        
        console.log('Admin Dashboard initialized');
    }    initializeUI() {
        // Initialize sidebar navigation
        this.initSidebarNavigation();
        
        // Initialize file view controls
        this.initFileViewControls();
        
        // Initialize search and filters
        this.initSearchAndFilters();
        
        // Initialize upload functionality
        this.initUploadFunctionality();
        
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
        });        // Sidebar toggle for mobile and desktop
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                const sidebar = document.querySelector('.sidebar');
                
                if (window.innerWidth <= 768) {
                    // Mobile: Show/hide sidebar with overlay
                    sidebar.classList.toggle('open');
                    const overlay = document.querySelector('.mobile-overlay');
                    if (overlay) {
                        overlay.classList.toggle('active');
                    }
                } else {
                    // Desktop: Collapse/expand sidebar
                    sidebar.classList.toggle('collapsed');
                }
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

        // Handle window resize for responsive layout
        window.addEventListener('resize', () => {
            this.handleWindowResize();
        });
    }    handleWindowResize() {
        // Add transitioning class for smooth animations
        const appContainer = document.querySelector('.app-container');
        appContainer.classList.add('layout-transitioning');
        
        // Debounce resize events for performance
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            // Detect window state changes
            this.detectWindowState();
            
            // Force layout recalculation
            this.forceLayoutRecalculation();
            
            // Ensure proper sidebar state on resize
            const sidebar = document.querySelector('.sidebar');
            const mainContent = document.querySelector('.main-content');
            
            if (window.innerWidth <= 768) {
                // Mobile layout
                sidebar.classList.add('mobile-layout');
                mainContent.classList.add('mobile-layout');
                this.createMobileOverlay();
            } else {
                // Desktop layout
                sidebar.classList.remove('mobile-layout');
                mainContent.classList.remove('mobile-layout');
                this.removeMobileOverlay();
            }
            
            // Update grid layout if in grid view
            if (this.currentView === 'grid') {
                this.adjustGridColumns();
            }
            
            // Remove transitioning class after animation
            setTimeout(() => {
                appContainer.classList.remove('layout-transitioning');
            }, 300);
            
            this.logActivity('🔄 Layout adjusted for window resize', 'system');
        }, 150);
    }

    detectWindowState() {
        const isMaximized = window.outerWidth === screen.availWidth && window.outerHeight === screen.availHeight;
        const body = document.body;
        
        if (isMaximized) {
            body.classList.add('window-maximized');
        } else {
            body.classList.remove('window-maximized');
        }
    }

    createMobileOverlay() {
        if (!document.querySelector('.mobile-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'mobile-overlay';
            overlay.addEventListener('click', () => {
                this.closeMobileSidebar();
            });
            document.body.appendChild(overlay);
        }
    }

    removeMobileOverlay() {
        const overlay = document.querySelector('.mobile-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    closeMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.mobile-overlay');
        
        sidebar.classList.remove('open');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    adjustGridColumns() {
        const filesGrid = document.getElementById('files-grid');
        if (!filesGrid) return;
        
        const containerWidth = filesGrid.clientWidth;
        let columns;
        
        if (containerWidth < 600) {
            columns = 2;
        } else if (containerWidth < 900) {
            columns = 3;
        } else if (containerWidth < 1200) {
            columns = 4;
        } else if (containerWidth < 1600) {
            columns = 5;
        } else {
            columns = 6;
        }
        
        filesGrid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    }    async checkAuth() {
        try {
            const response = await fetch(`${this.serverUrl}/files`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });

            if (response.ok) {
                this.isAuthenticated = true;
                this.logActivity('🔐 Authentication successful', 'system');
            } else if (response.status === 401) {
                this.isAuthenticated = false;
                this.logActivity('❌ Authentication failed', 'error');
                this.showToast('Authentication failed. Please check API key.', 'error');
            }
        } catch (error) {
            this.isAuthenticated = false;
            this.logActivity(`❌ Connection error: ${error.message}`, 'error');
            this.showToast('Could not connect to server', 'error');
        }
    }

    async testApiKeyConnection(testKey) {
        try {
            this.showToast('Testing API key...', 'info');
            
            const response = await fetch(`${this.serverUrl}/files`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${testKey}`
                }
            });

            if (response.ok) {
                this.showToast('✅ API key is valid', 'success');
                this.logActivity('API key test successful', 'system');
            } else if (response.status === 401) {
                this.showToast('❌ Invalid API key', 'error');
                this.logActivity('API key test failed - invalid key', 'error');
            } else {
                this.showToast(`❌ Server error: ${response.status}`, 'error');
                this.logActivity(`API key test failed - server error: ${response.status}`, 'error');
            }
        } catch (error) {
            this.showToast('❌ Connection error: Cannot reach server', 'error');
            this.logActivity(`API key test failed - connection error: ${error.message}`, 'error');
        }
    }    async loadDashboardData() {
        this.showLoading('Loading dashboard data...');
        
        try {
            // Load files from server
            this.showLoading('Loading files...');
            await this.loadRealFiles();
            
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

    async loadRealFiles() {
        if (this.isLoading) return;
        this.isLoading = true;
        
        try {
            // Show loading with progress
            this.showLoading('Loading files...');
            
            const response = await fetch(`${this.serverUrl}/files`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.files = Array.isArray(data) ? data : data.files || [];
                
                // Sort files by upload time (newest first)
                this.files.sort((a, b) => new Date(b.upload_time || b.created_at) - new Date(a.upload_time || a.created_at));
                
                // Initialize pagination
                this.initializePagination();
                
                // Filter and display files
                this.filterFiles();
                this.updateFileDisplay();
                this.addFileOperations();
                
                // Setup lazy loading
                this.setupLazyLoading();
                
                if (this.files.length > 0) {
                    this.logActivity(`📁 Loaded ${this.files.length} files from server`, 'info');
                } else {
                    this.logActivity('📂 No files found on server', 'info');
                }
                
                // Hide loading
                this.hideLoading();
                
            } else if (response.status === 401) {
                throw new Error('Authentication failed - please check API key');
            } else {
                throw new Error(`Server responded with status: ${response.status}`);
            }
        } catch (error) {
            console.warn('Failed to load real files, using sample data:', error.message);
            
            // Create sample data for demo purposes
            this.files = this.generateSampleFiles();
            this.initializePagination();
            this.filterFiles();
            this.updateFileDisplay();
            this.addFileOperations();
            this.setupLazyLoading();
            
            this.logActivity('⚠️ Using demo data - server connection failed', 'warning');
            this.showToast('Using demo data - check server connection', 'warning');
            this.hideLoading();
        } finally {
            this.isLoading = false;
        }
    }

    initializePagination() {
        this.totalPages = Math.ceil(this.files.length / this.itemsPerPage);
        this.currentPage = 1;
        this.updatePaginationControls();
    }

    setupLazyLoading() {
        // Setup intersection observer for lazy loading thumbnails
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }

        this.intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.dataset.src;
                        if (src && !this.loadedThumbnails.has(src)) {
                          img.src = src;
                          img.classList.remove('lazy');
                          this.loadedThumbnails.add(src);
                          this.intersectionObserver.unobserve(img);
                        }
                    }
                });
            },
            {
                rootMargin: '50px 0px',
                threshold: 0.1
            }
        );
    }

    filterFiles() {
        this.filteredFiles = this.files.filter(file => {
            const matchesSearch = this.searchQuery === '' || 
                file.original_filename.toLowerCase().includes(this.searchQuery) ||
                file.file_type.toLowerCase().includes(this.searchQuery);
            
            const matchesFilter = this.currentFilter === 'all' || 
                this.getFileCategory(file.file_type) === this.currentFilter;
            
            return matchesSearch && matchesFilter;
        });
        
        // Reset pagination when filtering
        this.currentPage = 1;
        this.totalPages = Math.ceil(this.filteredFiles.length / this.itemsPerPage);
        this.updatePaginationControls();
        this.updateFileDisplay();
    }

    updateFileDisplay() {
        // Performance: Only render visible items
        if (this.currentView === 'grid') {
            this.updateGridView();
        } else {
            this.updateListView();
        }
        
        // Update stats
        this.updateStatsCards();
    }

    updateGridView() {
        const filesGrid = document.getElementById('files-grid');
        const filesList = document.getElementById('files-list');
        
        if (!filesGrid) return;
        
        // Show grid, hide list
        filesGrid.style.display = 'grid';
        if (filesList) filesList.style.display = 'none';
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageFiles = this.filteredFiles.slice(startIndex, endIndex);
        
        // Clear grid with fade animation
        filesGrid.style.opacity = '0.5';
        setTimeout(() => {
            filesGrid.innerHTML = '';
            
            if (this.filteredFiles.length === 0) {
                filesGrid.innerHTML = `
                    <div class="no-files-message">
                        <div class="no-files-icon">
                            <i class="fas fa-folder-open"></i>
                        </div>
                        <h3>No files found</h3>
                        <p>Upload some files to get started or adjust your filters</p>
                        <button class="upload-btn" onclick="uploadFile()">
                            <i class="fas fa-cloud-upload-alt"></i>
                            Upload Files
                        </button>
                    </div>
                `;
                filesGrid.style.opacity = '1';
                return;
            }
            
            // Render files for current page
            pageFiles.forEach((file, index) => {
                const fileCard = this.createFileCard(file, startIndex + index);
                filesGrid.appendChild(fileCard);
            });
            
            // Setup lazy loading for new images
            this.setupLazyLoadingForImages();
            
            filesGrid.style.opacity = '1';
        }, 100);
    }

    createFileCard(file, index) {
        const fileCard = document.createElement('div');
        fileCard.className = 'file-card';
        fileCard.style.animationDelay = `${(index % this.itemsPerPage) * 50}ms`;
        
        // Use lazy loading for thumbnails
        const thumbnailHtml = file.has_thumbnail ? 
            `<img class="file-thumbnail lazy" data-src="${file.thumbnail_url}" alt="${file.original_filename}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
             <div class="file-icon" style="display: none;">${this.getFileIcon(file.file_type)}</div>` :
            `<div class="file-icon">${this.getFileIcon(file.file_type)}</div>`;
        
        fileCard.innerHTML = `
            <div class="file-preview" onclick="adminDashboard.previewFile('${file.file_id}')">
                ${thumbnailHtml}
                <div class="file-overlay">
                    <button class="overlay-btn" onclick="event.stopPropagation(); adminDashboard.previewFile('${file.file_id}')" title="Quick Preview">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
            <div class="file-info">
                <div class="file-name" title="${file.original_filename}">
                    ${this.truncateText(file.original_filename, 25)}
                </div>
                <div class="file-details">
                    <span class="file-size">${this.formatFileSize(file.file_size)}</span>
                    <span class="file-date">${this.formatRelativeDate(file.upload_time)}</span>
                </div>
            </div>
            <div class="file-actions">
                <button class="action-btn preview" onclick="adminDashboard.previewFile('${file.file_id}')" title="Preview">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn copy" onclick="adminDashboard.copyFileLink('${file.file_id}')" title="Copy Link">
                    <i class="fas fa-link"></i>
                </button>
                <button class="action-btn download" onclick="adminDashboard.downloadFile('${file.file_id}')" title="Download">
                    <i class="fas fa-download"></i>
                </button>
                <button class="action-btn delete" onclick="adminDashboard.deleteFile('${file.file_id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        return fileCard;
    }

    setupLazyLoadingForImages() {
        const lazyImages = document.querySelectorAll('img.lazy');
        lazyImages.forEach(img => {
            this.intersectionObserver.observe(img);
        });
    }

    updatePaginationControls() {
        const paginationContainer = document.getElementById('pagination-controls');
        if (!paginationContainer) {
            this.createPaginationControls();
            return;
        }

        if (this.totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }

        paginationContainer.style.display = 'flex';
        paginationContainer.innerHTML = '';

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = `pagination-btn ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.onclick = () => this.goToPage(this.currentPage - 1);
        paginationContainer.appendChild(prevBtn);

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);

        if (startPage > 1) {
            const firstBtn = document.createElement('button');
            firstBtn.className = 'pagination-btn';
            firstBtn.textContent = '1';
            firstBtn.onclick = () => this.goToPage(1);
            paginationContainer.appendChild(firstBtn);

            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                paginationContainer.appendChild(ellipsis);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `pagination-btn ${i === this.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => this.goToPage(i);
            paginationContainer.appendChild(pageBtn);
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                paginationContainer.appendChild(ellipsis);
            }

            const lastBtn = document.createElement('button');
            lastBtn.className = 'pagination-btn';
            lastBtn.textContent = this.totalPages;
            lastBtn.onclick = () => this.goToPage(this.totalPages);
            paginationContainer.appendChild(lastBtn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = `pagination-btn ${this.currentPage === this.totalPages ? 'disabled' : ''}`;
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.onclick = () => this.goToPage(this.currentPage + 1);
        paginationContainer.appendChild(nextBtn);

        // Page info
        const pageInfo = document.createElement('div');
        pageInfo.className = 'pagination-info';
        pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages} (${this.filteredFiles.length} files)`;
        paginationContainer.appendChild(pageInfo);
    }

    createPaginationControls() {
        const filesSection = document.querySelector('#files-tab .files-section');
        if (!filesSection) return;

        const paginationHTML = `
            <div id="pagination-controls" class="pagination-controls">
                <!-- Pagination buttons will be generated here -->
            </div>
        `;

        filesSection.insertAdjacentHTML('beforeend', paginationHTML);
        this.updatePaginationControls();
    }

    goToPage(page) {
        if (page < 1 || page > this.totalPages || page === this.currentPage) return;
        
        this.currentPage = page;
        this.updateFileDisplay();
        this.updatePaginationControls();
        
        // Scroll to top of files section
        const filesSection = document.getElementById('files-grid') || document.getElementById('files-list');
        if (filesSection) {
            filesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        this.logActivity(`📄 Navigated to page ${page}`, 'navigation');
    }

    // Force layout recalculation
    forceLayoutRecalculation() {
        const appContainer = document.querySelector('.app-container');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        // Temporarily hide and show to force reflow
        appContainer.style.display = 'none';
        appContainer.offsetHeight; // Force reflow
        appContainer.style.display = 'flex';
        
        // Trigger resize event to update layout
        window.dispatchEvent(new Event('resize'));
        
        this.logActivity('🔧 Layout recalculation forced', 'system');
    }

    // Initialize window state detection
    initWindowStateDetection() {
        // Detect initial window state
        this.detectWindowState();
        
        // Listen for window state changes
        window.addEventListener('resize', () => {
            this.detectWindowState();
        });
        
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => {
                    this.forceLayoutRecalculation();
                }, 100);
            }
        });
    }
}

// Global Functions for HTML Integration
let adminDashboard;

// Initialize admin dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});

// Global functions called from HTML
function switchTab(tabName) {
    if (adminDashboard) {
        adminDashboard.switchTab(tabName);
    }
}

function refreshData() {
    if (adminDashboard) {
        adminDashboard.refreshData();
        adminDashboard.showToast('Data refreshed', 'success');
    }
}

function uploadFile() {
    if (adminDashboard) {
        adminDashboard.showUploadModal();
        adminDashboard.logActivity('Upload modal opened', 'action');
    }
}

function cleanupOldFiles() {
    if (adminDashboard) {
        adminDashboard.showToast('Cleanup initiated', 'success');
        adminDashboard.logActivity('Cleanup old files initiated', 'system');
    }
}

function exportLogs() {
    if (adminDashboard) {
        const logData = JSON.stringify(adminDashboard.activityLog, null, 2);
        const blob = new Blob([logData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity_log_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        adminDashboard.showToast('Activity log exported', 'success');
        adminDashboard.logActivity('Activity log exported', 'action');
    }
}

function clearLog() {
    if (adminDashboard && confirm('Are you sure you want to clear the activity log?')) {
        adminDashboard.activityLog = [];
        adminDashboard.updateActivityLog();
        adminDashboard.updateRecentActivity();
        adminDashboard.showToast('Activity log cleared', 'info');
        adminDashboard.logActivity('Activity log cleared', 'system');
    }
}

function saveSettings() {
    if (adminDashboard) {
        adminDashboard.saveSettings();
    }
}

function resetSettings() {
    if (adminDashboard && confirm('Are you sure you want to reset all settings to default?')) {
        adminDashboard.resetSettings();
    }
}

function applyPreset(preset) {
    if (adminDashboard) {
        adminDashboard.showToast(`${preset} theme applied`, 'success');
        adminDashboard.logActivity(`Applied ${preset} theme preset`, 'setting');
        
        // Add preset classes to body
        document.body.className = document.body.className.replace(/theme-\w+/, '');
        document.body.classList.add(`theme-${preset}`);
    }
}

function closePreview() {
    if (adminDashboard) {
        adminDashboard.hideModal('file-preview-modal');
    }
}

function downloadFileFromPreview() {
    if (adminDashboard) {
        adminDashboard.showToast('Download started', 'success');
        adminDashboard.logActivity('File downloaded from preview', 'action');
    }
}

function copyLinkFromPreview() {
    if (adminDashboard) {
        navigator.clipboard.writeText(window.location.href).then(() => {
            adminDashboard.showToast('Link copied to clipboard', 'success');
            adminDashboard.logActivity('File link copied from preview', 'action');
        });
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('adminAuth');
        window.location.href = '/admin/login';
    }
}

function testApiKey() {
    if (adminDashboard) {
        const apiKeyInput = document.getElementById('api-key-setting');
        if (apiKeyInput && apiKeyInput.value.trim()) {
            const testKey = apiKeyInput.value.trim();
            adminDashboard.testApiKeyConnection(testKey);
        } else {
            adminDashboard.showToast('Please enter an API key to test', 'warning');
        }
    }
}