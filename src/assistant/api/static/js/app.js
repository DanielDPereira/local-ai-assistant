/**
 * Local AI Assistant - Dashboard App Logic
 */

class DashboardApp {
    constructor() {
        this.currentView = 'overview';
        this.cache = new Map();
        
        // DOM Elements
        this.elements = {
            navItems: document.querySelectorAll('.nav-item'),
            pageTitle: document.getElementById('page-title'),
            contentArea: document.getElementById('content-area'),
            loadingState: document.getElementById('loading-state'),
            errorState: document.getElementById('error-state'),
            errorMessage: document.getElementById('error-message'),
            retryBtn: document.getElementById('retry-btn'),
            statusIndicator: document.querySelector('.status-indicator'),
            statusText: document.getElementById('status-text')
        };
        
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.checkHealth();
        
        // Initial load based on hash or default
        const hash = window.location.hash.substring(1);
        if (hash && document.querySelector(`.nav-item[data-target="${hash}"]`)) {
            this.navigate(hash);
        } else {
            this.navigate('overview');
        }
        
        // Setup retry button
        this.elements.retryBtn.addEventListener('click', () => {
            this.loadViewData(this.currentView);
        });
        
        // Check health periodically
        setInterval(() => this.checkHealth(), 30000);
    }
    
    setupNavigation() {
        this.elements.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const target = e.currentTarget.getAttribute('data-target');
                if (target !== this.currentView) {
                    this.navigate(target);
                }
            });
        });
        
        // Handle browser back/forward
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash && hash !== this.currentView) {
                this.navigate(hash, false);
            }
        });
    }
    
    navigate(view, updateHash = true) {
        this.currentView = view;
        
        if (updateHash) {
            window.location.hash = view;
        }
        
        // Update nav UI
        this.elements.navItems.forEach(item => {
            if (item.getAttribute('data-target') === view) {
                item.classList.add('active');
                this.elements.pageTitle.textContent = item.textContent.trim();
            } else {
                item.classList.remove('active');
            }
        });
        
        this.loadViewData(view);
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                this.elements.statusIndicator.className = 'status-indicator online';
                this.elements.statusText.textContent = 'System Online';
            } else {
                throw new Error('System unhealthy');
            }
        } catch (error) {
            this.elements.statusIndicator.className = 'status-indicator offline';
            this.elements.statusText.textContent = 'System Offline';
        }
    }
    
    showLoading() {
        this.elements.contentArea.classList.add('hidden');
        this.elements.errorState.classList.add('hidden');
        this.elements.loadingState.classList.remove('hidden');
    }
    
    showError(message) {
        this.elements.loadingState.classList.add('hidden');
        this.elements.contentArea.classList.add('hidden');
        this.elements.errorState.classList.remove('hidden');
        this.elements.errorMessage.textContent = message;
    }
    
    showContent() {
        this.elements.loadingState.classList.add('hidden');
        this.elements.errorState.classList.add('hidden');
        this.elements.contentArea.classList.remove('hidden');
    }
    
    async loadViewData(view) {
        this.showLoading();
        
        try {
            let data;
            
            // For now, since endpoints are not returning real HTML,
            // we just show a placeholder until we implement each view
            // in subsequent tasks.
            this.elements.contentArea.innerHTML = `
                <div class="dashboard-grid">
                    <div class="card">
                        <h3>View: ${view}</h3>
                        <p style="color: var(--text-muted); margin-top: 8px;">
                            This view will be implemented in upcoming tasks.
                        </p>
                    </div>
                </div>
            `;
            
            this.showContent();
        } catch (error) {
            console.error('Error loading view:', error);
            this.showError(`Failed to load ${view} data: ${error.message}`);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
});
