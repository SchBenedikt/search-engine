/**
 * Advanced Search Features
 * Enhanced search interface with filters, sorting, and result management
 */

class AdvancedSearch {
    constructor() {
        this.filters = {
            dateRange: 'any',
            fileType: 'any',
            language: 'any',
            domain: '',
            sort: 'relevance'
        };
        this.init();
    }

    init() {
        this.createAdvancedSearchInterface();
        this.setupEventListeners();
        this.enhanceSearchResults();
    }

    createAdvancedSearchInterface() {
        // Add advanced search toggle to existing search forms
        const searchForms = document.querySelectorAll('form[action="/search"]');
        
        searchForms.forEach(form => {
            if (!form.querySelector('.advanced-search-toggle')) {
                this.addAdvancedSearchToggle(form);
            }
        });
    }

    addAdvancedSearchToggle(form) {
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'advanced-search-container';
        
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'advanced-search-toggle';
        toggle.innerHTML = '⚙️ Advanced Search';
        toggle.style.cssText = `
            background: none;
            border: none;
            color: #007bff;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            padding: 5px 0;
            text-decoration: underline;
        `;

        const panel = this.createAdvancedSearchPanel();
        panel.style.display = 'none';

        toggle.addEventListener('click', () => {
            const isVisible = panel.style.display !== 'none';
            panel.style.display = isVisible ? 'none' : 'block';
            toggle.innerHTML = isVisible ? '⚙️ Advanced Search' : '⚙️ Hide Advanced';
        });

        toggleContainer.appendChild(toggle);
        toggleContainer.appendChild(panel);
        
        form.appendChild(toggleContainer);
    }

    createAdvancedSearchPanel() {
        const panel = document.createElement('div');
        panel.className = 'advanced-search-panel';
        panel.innerHTML = `
            <div class="advanced-search-content">
                <h4>Advanced Search Options</h4>
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Date Range:</label>
                        <select name="dateRange" id="dateRange">
                            <option value="any">Any time</option>
                            <option value="day">Past 24 hours</option>
                            <option value="week">Past week</option>
                            <option value="month">Past month</option>
                            <option value="year">Past year</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>File Type:</label>
                        <select name="fileType" id="fileType">
                            <option value="any">Any format</option>
                            <option value="pdf">PDF</option>
                            <option value="doc">Word</option>
                            <option value="ppt">PowerPoint</option>
                            <option value="xls">Excel</option>
                            <option value="txt">Text</option>
                        </select>
                    </div>
                </div>
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Language:</label>
                        <select name="language" id="language">
                            <option value="any">Any language</option>
                            <option value="en">English</option>
                            <option value="de">German</option>
                            <option value="fr">French</option>
                            <option value="es">Spanish</option>
                            <option value="it">Italian</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Sort by:</label>
                        <select name="sort" id="sort">
                            <option value="relevance">Relevance</option>
                            <option value="date">Date</option>
                            <option value="popularity">Popularity</option>
                            <option value="title">Title</option>
                        </select>
                    </div>
                </div>
                <div class="filter-row">
                    <div class="filter-group full-width">
                        <label>Search within domain:</label>
                        <input type="text" name="domain" id="domain" placeholder="e.g., wikipedia.org">
                    </div>
                </div>
                <div class="filter-actions">
                    <button type="button" class="btn-reset-filters">Reset Filters</button>
                    <button type="button" class="btn-apply-filters">Apply Filters</button>
                </div>
            </div>
        `;

        panel.style.cssText = `
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-top: 15px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        `;

        // Add CSS for the panel content
        const style = document.createElement('style');
        style.textContent = `
            .advanced-search-content h4 {
                margin: 0 0 20px 0;
                color: #333;
                font-size: 18px;
                font-weight: 600;
            }
            .filter-row {
                display: flex;
                gap: 20px;
                margin-bottom: 15px;
            }
            .filter-group {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .filter-group.full-width {
                flex: 2;
            }
            .filter-group label {
                font-weight: 500;
                margin-bottom: 5px;
                color: #555;
                font-size: 14px;
            }
            .filter-group select,
            .filter-group input {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            .filter-actions {
                display: flex;
                gap: 10px;
                margin-top: 20px;
                justify-content: flex-end;
            }
            .btn-reset-filters,
            .btn-apply-filters {
                padding: 8px 16px;
                border: 1px solid #007bff;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s ease;
            }
            .btn-reset-filters {
                background: white;
                color: #007bff;
            }
            .btn-reset-filters:hover {
                background: #f8f9fa;
            }
            .btn-apply-filters {
                background: #007bff;
                color: white;
            }
            .btn-apply-filters:hover {
                background: #0056b3;
            }
            @media (max-width: 768px) {
                .filter-row {
                    flex-direction: column;
                    gap: 10px;
                }
                .filter-actions {
                    justify-content: stretch;
                }
                .btn-reset-filters,
                .btn-apply-filters {
                    flex: 1;
                }
            }
        `;

        if (!document.querySelector('#advanced-search-styles')) {
            style.id = 'advanced-search-styles';
            document.head.appendChild(style);
        }

        // Setup filter event listeners
        this.setupFilterListeners(panel);

        return panel;
    }

    setupFilterListeners(panel) {
        const resetBtn = panel.querySelector('.btn-reset-filters');
        const applyBtn = panel.querySelector('.btn-apply-filters');

        resetBtn.addEventListener('click', () => {
            this.resetFilters(panel);
        });

        applyBtn.addEventListener('click', () => {
            this.applyFilters(panel);
        });

        // Auto-save filter changes
        panel.querySelectorAll('select, input').forEach(element => {
            element.addEventListener('change', () => {
                this.saveFilterState(panel);
            });
        });

        // Load saved filter state
        this.loadFilterState(panel);
    }

    resetFilters(panel) {
        panel.querySelector('#dateRange').value = 'any';
        panel.querySelector('#fileType').value = 'any';
        panel.querySelector('#language').value = 'any';
        panel.querySelector('#sort').value = 'relevance';
        panel.querySelector('#domain').value = '';

        this.filters = {
            dateRange: 'any',
            fileType: 'any',
            language: 'any',
            domain: '',
            sort: 'relevance'
        };

        this.saveFilterState(panel);
    }

    applyFilters(panel) {
        this.filters.dateRange = panel.querySelector('#dateRange').value;
        this.filters.fileType = panel.querySelector('#fileType').value;
        this.filters.language = panel.querySelector('#language').value;
        this.filters.sort = panel.querySelector('#sort').value;
        this.filters.domain = panel.querySelector('#domain').value;

        // Apply filters to current search
        this.refreshSearchWithFilters();

        // Award points for using advanced search
        if (typeof addUserPoints === 'function') {
            addUserPoints(8, 'advanced_search', 'Used advanced search filters');
        }
    }

    saveFilterState(panel) {
        const state = {
            dateRange: panel.querySelector('#dateRange').value,
            fileType: panel.querySelector('#fileType').value,
            language: panel.querySelector('#language').value,
            sort: panel.querySelector('#sort').value,
            domain: panel.querySelector('#domain').value
        };

        localStorage.setItem('search_filters', JSON.stringify(state));
    }

    loadFilterState(panel) {
        const savedState = localStorage.getItem('search_filters');
        if (savedState) {
            const state = JSON.parse(savedState);
            panel.querySelector('#dateRange').value = state.dateRange || 'any';
            panel.querySelector('#fileType').value = state.fileType || 'any';
            panel.querySelector('#language').value = state.language || 'any';
            panel.querySelector('#sort').value = state.sort || 'relevance';
            panel.querySelector('#domain').value = state.domain || '';

            this.filters = state;
        }
    }

    refreshSearchWithFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        const currentQuery = urlParams.get('query');

        if (currentQuery) {
            // Build new URL with filters
            const newParams = new URLSearchParams();
            newParams.set('query', currentQuery);
            
            Object.keys(this.filters).forEach(key => {
                if (this.filters[key] && this.filters[key] !== 'any') {
                    newParams.set(key, this.filters[key]);
                }
            });

            // Redirect to filtered search
            window.location.href = `/search?${newParams.toString()}`;
        }
    }

    enhanceSearchResults() {
        // Add result management features
        this.addResultActions();
        this.addResultPreview();
        this.addBulkActions();
    }

    addResultActions() {
        setTimeout(() => {
            const results = document.querySelectorAll('.search-result-item');
            
            results.forEach((result, index) => {
                if (!result.querySelector('.result-actions')) {
                    const actions = this.createResultActions(result, index);
                    result.appendChild(actions);
                }
            });
        }, 500);
    }

    createResultActions(result, index) {
        const actions = document.createElement('div');
        actions.className = 'result-actions';
        actions.innerHTML = `
            <button class="action-btn preview-btn" title="Quick Preview">
                👁️
            </button>
            <button class="action-btn share-btn" title="Share">
                📤
            </button>
            <button class="action-btn save-btn" title="Save for Later">
                📌
            </button>
        `;

        actions.style.cssText = `
            position: absolute;
            top: 10px;
            right: 50px;
            display: flex;
            gap: 5px;
            opacity: 0;
            transition: opacity 0.2s ease;
        `;

        // Add CSS for action buttons
        const style = document.createElement('style');
        style.textContent = `
            .search-result-item {
                position: relative;
            }
            .search-result-item:hover .result-actions {
                opacity: 1;
            }
            .action-btn {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                width: 28px;
                height: 28px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .action-btn:hover {
                background: #f8f9fa;
                transform: translateY(-1px);
            }
        `;

        if (!document.querySelector('#result-actions-styles')) {
            style.id = 'result-actions-styles';
            document.head.appendChild(style);
        }

        // Setup action listeners
        actions.querySelector('.preview-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.showResultPreview(result);
        });

        actions.querySelector('.share-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.shareResult(result);
        });

        actions.querySelector('.save-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.saveResult(result);
        });

        return actions;
    }

    showResultPreview(result) {
        const url = result.querySelector('a')?.href;
        if (!url) return;

        // Create preview modal
        const modal = document.createElement('div');
        modal.className = 'preview-modal';
        modal.innerHTML = `
            <div class="preview-content">
                <div class="preview-header">
                    <h3>Quick Preview</h3>
                    <button class="close-preview">&times;</button>
                </div>
                <div class="preview-body">
                    <iframe src="${url}" frameborder="0"></iframe>
                </div>
                <div class="preview-footer">
                    <a href="${url}" target="_blank" class="btn-open-full">Open Full Page</a>
                </div>
            </div>
        `;

        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        // Add CSS for preview modal
        const style = document.createElement('style');
        style.textContent = `
            .preview-content {
                background: white;
                border-radius: 8px;
                width: 90%;
                height: 90%;
                max-width: 1200px;
                display: flex;
                flex-direction: column;
            }
            .preview-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
            }
            .preview-header h3 {
                margin: 0;
                font-size: 18px;
            }
            .close-preview {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                padding: 5px;
            }
            .preview-body {
                flex: 1;
                overflow: hidden;
            }
            .preview-body iframe {
                width: 100%;
                height: 100%;
            }
            .preview-footer {
                padding: 15px 20px;
                border-top: 1px solid #eee;
                text-align: right;
            }
            .btn-open-full {
                background: #007bff;
                color: white;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
            }
        `;

        if (!document.querySelector('#preview-modal-styles')) {
            style.id = 'preview-modal-styles';
            document.head.appendChild(style);
        }

        document.body.appendChild(modal);

        // Close modal functionality
        modal.querySelector('.close-preview').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    shareResult(result) {
        const url = result.querySelector('a')?.href;
        const title = result.querySelector('h3, .result-title')?.textContent || 'Search Result';

        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(url).then(() => {
                this.showToast('Link copied to clipboard!');
            });
        }

        // Award points for sharing
        if (typeof addUserPoints === 'function') {
            addUserPoints(3, 'result_shared', 'Shared search result');
        }
    }

    saveResult(result) {
        const url = result.querySelector('a')?.href;
        const title = result.querySelector('h3, .result-title')?.textContent || 'Search Result';

        // Save to local storage
        let savedResults = JSON.parse(localStorage.getItem('saved_results') || '[]');
        
        const savedResult = {
            title: title,
            url: url,
            timestamp: new Date().toISOString(),
            id: Date.now()
        };

        // Check if already saved
        if (!savedResults.some(item => item.url === url)) {
            savedResults.unshift(savedResult);
            localStorage.setItem('saved_results', JSON.stringify(savedResults));
            
            this.showToast('Result saved!');
            
            // Award points for saving
            if (typeof addUserPoints === 'function') {
                addUserPoints(5, 'result_saved', 'Saved search result');
            }
        } else {
            this.showToast('Result already saved!');
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 10000;
            animation: toastSlideIn 0.3s ease;
        `;

        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes toastSlideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;

        if (!document.querySelector('#toast-styles')) {
            style.id = 'toast-styles';
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    addBulkActions() {
        // Add bulk selection and actions to search results page
        if (window.location.pathname === '/search') {
            this.createBulkActionBar();
        }
    }

    createBulkActionBar() {
        const resultsContainer = document.querySelector('.search-results, #search-results');
        if (!resultsContainer || resultsContainer.querySelector('.bulk-actions')) return;

        const bulkBar = document.createElement('div');
        bulkBar.className = 'bulk-actions';
        bulkBar.innerHTML = `
            <div class="bulk-selection">
                <input type="checkbox" id="select-all" />
                <label for="select-all">Select All</label>
                <span class="selection-count">0 selected</span>
            </div>
            <div class="bulk-buttons">
                <button class="bulk-btn save-selected">Save Selected</button>
                <button class="bulk-btn share-selected">Share Selected</button>
                <button class="bulk-btn export-selected">Export Selected</button>
            </div>
        `;

        bulkBar.style.cssText = `
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;

        resultsContainer.insertBefore(bulkBar, resultsContainer.firstChild);

        // Setup bulk action functionality
        this.setupBulkActions(bulkBar);
    }

    setupBulkActions(bulkBar) {
        const selectAll = bulkBar.querySelector('#select-all');
        const countSpan = bulkBar.querySelector('.selection-count');

        // Add checkboxes to each result
        setTimeout(() => {
            const results = document.querySelectorAll('.search-result-item');
            results.forEach((result, index) => {
                if (!result.querySelector('.result-checkbox')) {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.className = 'result-checkbox';
                    checkbox.style.cssText = `
                        position: absolute;
                        top: 10px;
                        left: 10px;
                        z-index: 2;
                    `;
                    
                    checkbox.addEventListener('change', () => {
                        this.updateSelectionCount(countSpan);
                    });

                    result.appendChild(checkbox);
                }
            });
        }, 100);

        // Select all functionality
        selectAll.addEventListener('change', () => {
            const checkboxes = document.querySelectorAll('.result-checkbox');
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
            this.updateSelectionCount(countSpan);
        });

        // Bulk action buttons
        bulkBar.querySelector('.save-selected').addEventListener('click', () => {
            this.bulkSaveResults();
        });

        bulkBar.querySelector('.share-selected').addEventListener('click', () => {
            this.bulkShareResults();
        });

        bulkBar.querySelector('.export-selected').addEventListener('click', () => {
            this.bulkExportResults();
        });
    }

    updateSelectionCount(countSpan) {
        const selected = document.querySelectorAll('.result-checkbox:checked');
        countSpan.textContent = `${selected.length} selected`;
    }

    bulkSaveResults() {
        const selected = document.querySelectorAll('.result-checkbox:checked');
        let savedCount = 0;

        selected.forEach(checkbox => {
            const result = checkbox.closest('.search-result-item');
            const url = result.querySelector('a')?.href;
            const title = result.querySelector('h3, .result-title')?.textContent;

            if (url && title) {
                let savedResults = JSON.parse(localStorage.getItem('saved_results') || '[]');
                
                if (!savedResults.some(item => item.url === url)) {
                    savedResults.unshift({
                        title: title,
                        url: url,
                        timestamp: new Date().toISOString(),
                        id: Date.now() + savedCount
                    });
                    savedCount++;
                }
                
                localStorage.setItem('saved_results', JSON.stringify(savedResults));
            }
        });

        this.showToast(`${savedCount} results saved!`);

        // Award points for bulk save
        if (typeof addUserPoints === 'function' && savedCount > 0) {
            addUserPoints(savedCount * 2, 'bulk_save', `Bulk saved ${savedCount} results`);
        }
    }

    bulkShareResults() {
        const selected = document.querySelectorAll('.result-checkbox:checked');
        const urls = Array.from(selected).map(checkbox => {
            const result = checkbox.closest('.search-result-item');
            return result.querySelector('a')?.href;
        }).filter(url => url);

        if (urls.length > 0) {
            const shareText = `Check out these search results:\n\n${urls.join('\n')}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'Search Results',
                    text: shareText
                });
            } else {
                navigator.clipboard.writeText(shareText).then(() => {
                    this.showToast('Results copied to clipboard!');
                });
            }

            // Award points for bulk share
            if (typeof addUserPoints === 'function') {
                addUserPoints(urls.length, 'bulk_share', `Bulk shared ${urls.length} results`);
            }
        }
    }

    bulkExportResults() {
        const selected = document.querySelectorAll('.result-checkbox:checked');
        const results = Array.from(selected).map(checkbox => {
            const result = checkbox.closest('.search-result-item');
            return {
                title: result.querySelector('h3, .result-title')?.textContent || '',
                url: result.querySelector('a')?.href || '',
                description: result.querySelector('.result-description, p')?.textContent || '',
                exportDate: new Date().toISOString()
            };
        });

        if (results.length > 0) {
            const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `search-results-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);

            this.showToast(`${results.length} results exported!`);

            // Award points for export
            if (typeof addUserPoints === 'function') {
                addUserPoints(results.length, 'bulk_export', `Exported ${results.length} results`);
            }
        }
    }

    setupEventListeners() {
        // Listen for search form submissions to apply filters
        document.addEventListener('submit', (e) => {
            if (e.target.matches('form[action="/search"]')) {
                // Add current filters to form submission
                Object.keys(this.filters).forEach(key => {
                    if (this.filters[key] && this.filters[key] !== 'any') {
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = key;
                        input.value = this.filters[key];
                        e.target.appendChild(input);
                    }
                });
            }
        });
    }
}

// Initialize advanced search when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.advancedSearch = new AdvancedSearch();
});

// Export for use in other modules
window.AdvancedSearch = AdvancedSearch;