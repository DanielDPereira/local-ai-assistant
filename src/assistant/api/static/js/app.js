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
            if (view === 'overview') {
                await this.renderOverview();
            } else if (view === 'executions') {
                await this.renderExecutions();
            } else {
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
            }
        } catch (error) {
            console.error('Error loading view:', error);
            this.showError(`Failed to load ${view} data: ${error.message}`);
        }
    }
    
    async renderOverview() {
        const response = await fetch('/api/metrics/overview');
        if (!response.ok) throw new Error('Failed to fetch overview data');
        
        const data = await response.json();
        
        this.elements.contentArea.innerHTML = `
            <div class="dashboard-grid">
                <div class="stat-card">
                    <span class="stat-label">Total Executions</span>
                    <span class="stat-value">${data.total_executions}</span>
                </div>
                <div class="stat-card success">
                    <span class="stat-label">Success Rate</span>
                    <span class="stat-value">${data.success_rate.toFixed(1)}%</span>
                </div>
                <div class="stat-card danger">
                    <span class="stat-label">Failed Executions</span>
                    <span class="stat-value">${data.failed_executions}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Avg Duration</span>
                    <span class="stat-value">${(data.avg_duration_ms / 1000).toFixed(2)}s</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Total Tokens</span>
                    <span class="stat-value">${data.total_tokens.toLocaleString()}</span>
                </div>
                <div class="stat-card warning">
                    <span class="stat-label">Estimated Cost</span>
                    <span class="stat-value">$${data.total_cost.toFixed(4)}</span>
                </div>
            </div>
        `;
        
        this.showContent();
    }
    
    async renderExecutions() {
        const response = await fetch('/api/metrics/executions?limit=20');
        if (!response.ok) throw new Error('Failed to fetch executions data');
        
        const data = await response.json();
        
        let rowsHtml = '';
        if (data.items.length === 0) {
            rowsHtml = '<tr><td colspan="6" style="text-align: center;">No executions found</td></tr>';
        } else {
            rowsHtml = data.items.map(exec => {
                const statusClass = exec.status === 'DONE' ? 'success' : (exec.status === 'ERROR' ? 'danger' : 'warning');
                return `
                    <tr>
                        <td style="font-family: monospace;">${exec.id.substring(0, 8)}...</td>
                        <td>${new Date(exec.started_at).toLocaleString()}</td>
                        <td>${exec.model}</td>
                        <td><span class="status-badge ${statusClass}">${exec.status}</span></td>
                        <td>${(exec.duration_ms / 1000).toFixed(2)}s</td>
                        <td>$${exec.estimated_cost.toFixed(4)}</td>
                    </tr>
                `;
            }).join('');
        }
        
        this.elements.contentArea.innerHTML = `
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Started At</th>
                            <th>Model</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
        
        this.showContent();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
});
