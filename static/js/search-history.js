/**
 * Search History and Enhanced Search Features
 * Provides search history, favorites, and intelligent suggestions
 */

class SearchHistory {
    constructor() {
        this.maxHistory = 50;
        this.maxFavorites = 100;
        this.init();
    }

    init() {
        this.loadHistory();
        this.loadFavorites();
        this.setupEventListeners();
        this.createSearchHistoryDropdown();
    }

    loadHistory() {
        this.history = JSON.parse(localStorage.getItem('search_history') || '[]');
    }

    loadFavorites() {
        this.favorites = JSON.parse(localStorage.getItem('search_favorites') || '[]');
    }

    saveHistory() {
        localStorage.setItem('search_history', JSON.stringify(this.history));
    }

    saveFavorites() {
        localStorage.setItem('search_favorites', JSON.stringify(this.favorites));
    }

    addToHistory(query, url = null) {
        if (!query || query.trim() === '') return;

        const historyItem = {
            query: query.trim(),
            url: url,
            timestamp: new Date().toISOString(),
            id: Date.now()
        };

        // Remove duplicate if exists
        this.history = this.history.filter(item => item.query !== historyItem.query);
        
        // Add to beginning
        this.history.unshift(historyItem);
        
        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history = this.history.slice(0, this.maxHistory);
        }

        this.saveHistory();
        this.updateSearchDropdown();
    }

    addToFavorites(query, title = '', url = '') {
        if (!query || query.trim() === '') return;

        const favoriteItem = {
            query: query.trim(),
            title: title || query,
            url: url,
            timestamp: new Date().toISOString(),
            id: Date.now()
        };

        // Check if already exists
        if (this.favorites.some(item => item.query === favoriteItem.query)) {
            return false;
        }

        this.favorites.unshift(favoriteItem);
        
        // Limit favorites size
        if (this.favorites.length > this.maxFavorites) {
            this.favorites = this.favorites.slice(0, this.maxFavorites);
        }

        this.saveFavorites();
        return true;
    }

    removeFromFavorites(query) {
        this.favorites = this.favorites.filter(item => item.query !== query);
        this.saveFavorites();
    }

    isFavorite(query) {
        return this.favorites.some(item => item.query === query);
    }

    getRecentSearches(limit = 5) {
        return this.history.slice(0, limit);
    }

    getSearchSuggestions(input, limit = 8) {
        if (!input || input.length < 2) return [];

        const suggestions = [];
        const inputLower = input.toLowerCase();

        // Add from history
        const historyMatches = this.history
            .filter(item => item.query.toLowerCase().includes(inputLower))
            .slice(0, 4)
            .map(item => ({
                text: item.query,
                type: 'history',
                timestamp: item.timestamp
            }));

        suggestions.push(...historyMatches);

        // Add from favorites
        const favoriteMatches = this.favorites
            .filter(item => item.query.toLowerCase().includes(inputLower))
            .slice(0, 2)
            .map(item => ({
                text: item.query,
                type: 'favorite',
                title: item.title
            }));

        suggestions.push(...favoriteMatches);

        // Add trending/popular searches (simulated)
        const trendingSearches = [
            'artificial intelligence', 'machine learning', 'web development',
            'climate change', 'cryptocurrency', 'space exploration',
            'renewable energy', 'quantum computing', 'biotechnology', 'robotics'
        ];

        const trendingMatches = trendingSearches
            .filter(term => term.toLowerCase().includes(inputLower) && 
                   !suggestions.some(s => s.text === term))
            .slice(0, 2)
            .map(term => ({
                text: term,
                type: 'trending'
            }));

        suggestions.push(...trendingMatches);

        return suggestions.slice(0, limit);
    }

    createSearchHistoryDropdown() {
        const searchInputs = document.querySelectorAll('input[type="search"], input[name="query"]');
        
        searchInputs.forEach(input => {
            this.attachSearchDropdown(input);
        });
    }

    attachSearchDropdown(input) {
        const container = input.parentElement;
        if (container.querySelector('.search-suggestions')) return; // Already attached

        const dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;

        container.style.position = 'relative';
        container.appendChild(dropdown);

        // Input event listeners
        let searchTimeout;
        input.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.updateSearchDropdown(input, dropdown);
            }, 150);
        });

        input.addEventListener('focus', () => {
            this.updateSearchDropdown(input, dropdown);
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });

        // Handle keyboard navigation
        input.addEventListener('keydown', (e) => {
            const items = dropdown.querySelectorAll('.suggestion-item');
            const activeItem = dropdown.querySelector('.suggestion-item.active');
            let activeIndex = -1;

            if (activeItem) {
                activeIndex = Array.from(items).indexOf(activeItem);
            }

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    if (activeIndex < items.length - 1) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[activeIndex + 1].classList.add('active');
                    }
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (activeIndex > 0) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[activeIndex - 1].classList.add('active');
                    }
                    break;
                case 'Enter':
                    if (activeItem) {
                        e.preventDefault();
                        activeItem.click();
                    }
                    break;
                case 'Escape':
                    dropdown.style.display = 'none';
                    break;
            }
        });
    }

    updateSearchDropdown(input, dropdown) {
        if (!input || !dropdown) {
            // Find dropdown if not provided
            const container = input?.parentElement;
            dropdown = container?.querySelector('.search-suggestions');
            if (!dropdown) return;
        }

        const query = input.value.trim();
        
        if (query.length < 1) {
            // Show recent searches when empty
            const recentSearches = this.getRecentSearches(5);
            if (recentSearches.length > 0) {
                this.renderSuggestions(dropdown, recentSearches.map(item => ({
                    text: item.query,
                    type: 'history',
                    timestamp: item.timestamp
                })), input);
                dropdown.style.display = 'block';
            } else {
                dropdown.style.display = 'none';
            }
            return;
        }

        const suggestions = this.getSearchSuggestions(query);
        
        if (suggestions.length > 0) {
            this.renderSuggestions(dropdown, suggestions, input);
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    }

    renderSuggestions(dropdown, suggestions, input) {
        dropdown.innerHTML = '';

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            
            const iconMap = {
                'history': '🕐',
                'favorite': '⭐',
                'trending': '🔥'
            };

            item.innerHTML = `
                <div class="suggestion-content">
                    <span class="suggestion-icon">${iconMap[suggestion.type] || '🔍'}</span>
                    <span class="suggestion-text">${this.highlightMatch(suggestion.text, input.value)}</span>
                    ${suggestion.type === 'history' ? '<span class="suggestion-meta">Recent</span>' : ''}
                    ${suggestion.type === 'favorite' ? '<span class="suggestion-meta">Favorite</span>' : ''}
                    ${suggestion.type === 'trending' ? '<span class="suggestion-meta">Trending</span>' : ''}
                </div>
            `;

            item.style.cssText = `
                padding: 12px 16px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background-color 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: space-between;
            `;

            item.addEventListener('mouseenter', () => {
                dropdown.querySelectorAll('.suggestion-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            });

            item.addEventListener('click', () => {
                input.value = suggestion.text;
                dropdown.style.display = 'none';
                
                // Trigger search
                const form = input.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
                
                // Add to history
                this.addToHistory(suggestion.text);
                
                // Award points for search suggestion usage
                if (typeof addUserPoints === 'function') {
                    addUserPoints(3, 'suggestion_used', 'Used search suggestion');
                }
            });

            dropdown.appendChild(item);
        });

        // Add CSS for hover and active states
        const style = document.createElement('style');
        style.textContent = `
            .suggestion-item:hover,
            .suggestion-item.active {
                background-color: #f8f9fa;
            }
            .suggestion-content {
                display: flex;
                align-items: center;
                width: 100%;
            }
            .suggestion-icon {
                margin-right: 12px;
                font-size: 14px;
            }
            .suggestion-text {
                flex: 1;
                font-size: 14px;
            }
            .suggestion-meta {
                font-size: 12px;
                color: #666;
                background: #e9ecef;
                padding: 2px 8px;
                border-radius: 10px;
            }
        `;
        
        if (!document.querySelector('#suggestion-styles')) {
            style.id = 'suggestion-styles';
            document.head.appendChild(style);
        }
    }

    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    setupEventListeners() {
        // Listen for search form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('form') && e.target.querySelector('input[name="query"]')) {
                const queryInput = e.target.querySelector('input[name="query"]');
                if (queryInput && queryInput.value.trim()) {
                    this.addToHistory(queryInput.value.trim());
                }
            }
        });

        // Add favorite button functionality to search results
        this.addFavoriteButtons();
    }

    addFavoriteButtons() {
        // This would be called after search results are loaded
        // For now, we'll add it to be called manually
        setTimeout(() => {
            const searchResults = document.querySelectorAll('.search-result-item');
            searchResults.forEach(result => {
                if (!result.querySelector('.favorite-btn')) {
                    const favoriteBtn = this.createFavoriteButton(result);
                    result.appendChild(favoriteBtn);
                }
            });
        }, 1000);
    }

    createFavoriteButton(resultElement) {
        const btn = document.createElement('button');
        btn.className = 'favorite-btn';
        btn.innerHTML = '⭐';
        btn.title = 'Add to favorites';
        
        btn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const title = resultElement.querySelector('h3, .result-title')?.textContent || '';
            const url = resultElement.querySelector('a')?.href || '';
            const query = new URLSearchParams(window.location.search).get('query') || '';
            
            if (this.isFavorite(query)) {
                this.removeFromFavorites(query);
                btn.innerHTML = '☆';
                btn.title = 'Add to favorites';
                btn.style.color = '#666';
            } else {
                this.addToFavorites(query, title, url);
                btn.innerHTML = '⭐';
                btn.title = 'Remove from favorites';
                btn.style.color = '#ffd700';
                
                // Award points for favoriting
                if (typeof addUserPoints === 'function') {
                    addUserPoints(5, 'favorite_added', 'Added search to favorites');
                }
            }
        });

        return btn;
    }

    exportHistory() {
        const data = {
            history: this.history,
            favorites: this.favorites,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `search-history-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }

    importHistory(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.history) {
                    this.history = [...data.history, ...this.history].slice(0, this.maxHistory);
                    this.saveHistory();
                }
                if (data.favorites) {
                    this.favorites = [...data.favorites, ...this.favorites].slice(0, this.maxFavorites);
                    this.saveFavorites();
                }
                alert('Search history imported successfully!');
            } catch (error) {
                alert('Error importing search history. Please check the file format.');
            }
        };
        reader.readAsText(file);
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear your search history?')) {
            this.history = [];
            this.saveHistory();
            this.updateSearchDropdown();
        }
    }

    clearFavorites() {
        if (confirm('Are you sure you want to clear your favorites?')) {
            this.favorites = [];
            this.saveFavorites();
        }
    }
}

// Initialize search history when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.searchHistory = new SearchHistory();
});

// Export for use in other modules
window.SearchHistory = SearchHistory;