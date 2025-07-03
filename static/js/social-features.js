/**
 * Social Sharing and Collaboration Features
 * Advanced sharing capabilities and social features for the search engine
 */

class SocialFeatures {
    constructor() {
        this.shareHistory = [];
        this.collaborativeSearches = new Map();
        this.init();
    }

    init() {
        this.createSocialPanel();
        this.setupEventListeners();
        this.initializeCollaboration();
    }

    createSocialPanel() {
        // Add social sharing button to search results
        if (window.location.pathname.includes('/search')) {
            this.addSocialShareButton();
        }

        // Add collaboration features
        this.addCollaborationPanel();
    }

    addSocialShareButton() {
        const resultsContainer = document.querySelector('.search-results, #search-results');
        if (!resultsContainer) return;

        const sharePanel = document.createElement('div');
        sharePanel.className = 'social-share-panel';
        sharePanel.innerHTML = `
            <div class="share-controls">
                <button class="share-btn primary" id="share-search">
                    📤 Share Search
                </button>
                <button class="share-btn" id="create-collection">
                    📚 Create Collection
                </button>
                <button class="share-btn" id="collaborate">
                    👥 Collaborate
                </button>
            </div>
        `;

        sharePanel.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        `;

        // Add CSS for share controls
        const style = document.createElement('style');
        style.textContent = `
            .share-controls {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                align-items: center;
            }
            .share-btn {
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
            }
            .share-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }
            .share-btn.primary {
                background: rgba(255,255,255,0.9);
                color: #333;
            }
            .share-btn.primary:hover {
                background: white;
            }
            @media (max-width: 768px) {
                .share-controls {
                    justify-content: center;
                }
                .share-btn {
                    flex: 1;
                    min-width: 120px;
                }
            }
        `;

        if (!document.querySelector('#social-styles')) {
            style.id = 'social-styles';
            document.head.appendChild(style);
        }

        resultsContainer.parentNode.insertBefore(sharePanel, resultsContainer);

        // Setup button listeners
        this.setupSocialButtons(sharePanel);
    }

    setupSocialButtons(panel) {
        panel.querySelector('#share-search').addEventListener('click', () => {
            this.shareCurrentSearch();
        });

        panel.querySelector('#create-collection').addEventListener('click', () => {
            this.createSearchCollection();
        });

        panel.querySelector('#collaborate').addEventListener('click', () => {
            this.startCollaboration();
        });
    }

    shareCurrentSearch() {
        const currentUrl = window.location.href;
        const query = new URLSearchParams(window.location.search).get('query') || '';
        
        const shareData = {
            title: `Search Results for "${query}"`,
            text: `Check out these search results for "${query}"`,
            url: currentUrl
        };

        // Create share modal
        const modal = this.createShareModal(shareData);
        document.body.appendChild(modal);

        // Award points for sharing
        if (typeof addUserPoints === 'function') {
            addUserPoints(5, 'search_shared', 'Shared search results');
        }
    }

    createShareModal(shareData) {
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <div class="share-header">
                    <h3>Share Search Results</h3>
                    <button class="close-share">&times;</button>
                </div>
                <div class="share-body">
                    <div class="share-platforms">
                        <button class="platform-btn" data-platform="twitter">
                            <div class="platform-icon">🐦</div>
                            <div class="platform-name">Twitter</div>
                        </button>
                        <button class="platform-btn" data-platform="facebook">
                            <div class="platform-icon">📘</div>
                            <div class="platform-name">Facebook</div>
                        </button>
                        <button class="platform-btn" data-platform="linkedin">
                            <div class="platform-icon">💼</div>
                            <div class="platform-name">LinkedIn</div>
                        </button>
                        <button class="platform-btn" data-platform="reddit">
                            <div class="platform-icon">🤖</div>
                            <div class="platform-name">Reddit</div>
                        </button>
                        <button class="platform-btn" data-platform="email">
                            <div class="platform-icon">📧</div>
                            <div class="platform-name">Email</div>
                        </button>
                        <button class="platform-btn" data-platform="copy">
                            <div class="platform-icon">📋</div>
                            <div class="platform-name">Copy Link</div>
                        </button>
                    </div>
                    <div class="share-options">
                        <div class="share-option">
                            <label>
                                <input type="checkbox" id="include-filters" checked>
                                Include search filters
                            </label>
                        </div>
                        <div class="share-option">
                            <label>
                                <input type="checkbox" id="generate-qr">
                                Generate QR code
                            </label>
                        </div>
                    </div>
                    <div class="custom-message">
                        <label>Custom message (optional):</label>
                        <textarea placeholder="Add a personal note..."></textarea>
                    </div>
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

        // Add CSS for share modal
        const style = document.createElement('style');
        style.textContent = `
            .share-modal-content {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                max-height: 80vh;
                overflow-y: auto;
            }
            .share-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                border-bottom: 1px solid #eee;
            }
            .share-header h3 {
                margin: 0;
                font-size: 20px;
                color: #333;
            }
            .close-share {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                padding: 5px;
                color: #666;
            }
            .share-body {
                padding: 20px;
            }
            .share-platforms {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }
            .platform-btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 15px;
                border: 2px solid #f0f0f0;
                border-radius: 8px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .platform-btn:hover {
                border-color: #007bff;
                background: #f8f9ff;
                transform: translateY(-2px);
            }
            .platform-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }
            .platform-name {
                font-size: 14px;
                font-weight: 500;
                color: #333;
            }
            .share-options {
                margin-bottom: 20px;
            }
            .share-option {
                margin-bottom: 10px;
            }
            .share-option label {
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                font-size: 14px;
            }
            .custom-message label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
            }
            .custom-message textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                resize: vertical;
                min-height: 80px;
                font-family: inherit;
            }
            @media (max-width: 480px) {
                .share-platforms {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        `;

        if (!document.querySelector('#share-modal-styles')) {
            style.id = 'share-modal-styles';
            document.head.appendChild(style);
        }

        // Setup modal functionality
        this.setupShareModal(modal, shareData);

        return modal;
    }

    setupShareModal(modal, shareData) {
        // Close modal
        modal.querySelector('.close-share').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Platform sharing
        modal.querySelectorAll('.platform-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const platform = btn.dataset.platform;
                const customMessage = modal.querySelector('.custom-message textarea').value;
                this.shareToplatform(platform, shareData, customMessage);
            });
        });

        // QR code generation
        modal.querySelector('#generate-qr').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.generateQRCode(shareData.url, modal);
            } else {
                const qrContainer = modal.querySelector('.qr-container');
                if (qrContainer) qrContainer.remove();
            }
        });
    }

    shareToplatform(platform, shareData, customMessage = '') {
        const fullMessage = customMessage ? `${customMessage}\n\n${shareData.text}` : shareData.text;
        const encodedMessage = encodeURIComponent(fullMessage);
        const encodedUrl = encodeURIComponent(shareData.url);
        const encodedTitle = encodeURIComponent(shareData.title);

        let shareUrl = '';

        switch (platform) {
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?text=${encodedMessage}&url=${encodedUrl}`;
                break;
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedMessage}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}&title=${encodedTitle}&summary=${encodedMessage}`;
                break;
            case 'reddit':
                shareUrl = `https://reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`;
                break;
            case 'email':
                shareUrl = `mailto:?subject=${encodedTitle}&body=${encodedMessage}%0A%0A${encodedUrl}`;
                break;
            case 'copy':
                navigator.clipboard.writeText(shareData.url).then(() => {
                    this.showToast('Link copied to clipboard!');
                });
                return;
        }

        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }

        // Save to share history
        this.saveToShareHistory(platform, shareData);
    }

    generateQRCode(url, modal) {
        // Simple QR code generation using a service
        const qrContainer = document.createElement('div');
        qrContainer.className = 'qr-container';
        qrContainer.innerHTML = `
            <div class="qr-code">
                <h4>QR Code</h4>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(url)}" alt="QR Code">
                <p>Scan to share this search</p>
            </div>
        `;

        qrContainer.style.cssText = `
            margin-top: 20px;
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        `;

        modal.querySelector('.share-body').appendChild(qrContainer);
    }

    createSearchCollection() {
        const modal = document.createElement('div');
        modal.className = 'collection-modal';
        modal.innerHTML = `
            <div class="collection-modal-content">
                <div class="collection-header">
                    <h3>Create Search Collection</h3>
                    <button class="close-collection">&times;</button>
                </div>
                <div class="collection-body">
                    <div class="collection-form">
                        <div class="form-group">
                            <label>Collection Name:</label>
                            <input type="text" id="collection-name" placeholder="My Research Collection">
                        </div>
                        <div class="form-group">
                            <label>Description:</label>
                            <textarea id="collection-desc" placeholder="Describe your collection..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Privacy:</label>
                            <select id="collection-privacy">
                                <option value="private">Private (only you)</option>
                                <option value="public">Public (anyone can view)</option>
                                <option value="unlisted">Unlisted (link-only access)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Tags:</label>
                            <input type="text" id="collection-tags" placeholder="research, ai, technology (comma-separated)">
                        </div>
                    </div>
                    <div class="collection-preview">
                        <h4>Collection Preview</h4>
                        <div class="selected-results">
                            <!-- Selected results will be populated here -->
                        </div>
                    </div>
                </div>
                <div class="collection-footer">
                    <button class="btn-cancel">Cancel</button>
                    <button class="btn-create-collection">Create Collection</button>
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

        document.body.appendChild(modal);
        this.setupCollectionModal(modal);
    }

    setupCollectionModal(modal) {
        // Close modal functionality
        modal.querySelector('.close-collection').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelector('.btn-cancel').addEventListener('click', () => {
            modal.remove();
        });

        // Create collection
        modal.querySelector('.btn-create-collection').addEventListener('click', () => {
            this.saveCollection(modal);
        });

        // Populate selected results
        this.populateSelectedResults(modal);
    }

    populateSelectedResults(modal) {
        const selectedCheckboxes = document.querySelectorAll('.result-checkbox:checked');
        const previewContainer = modal.querySelector('.selected-results');

        if (selectedCheckboxes.length === 0) {
            previewContainer.innerHTML = '<p>No results selected. All current search results will be included.</p>';
            return;
        }

        previewContainer.innerHTML = '';
        selectedCheckboxes.forEach(checkbox => {
            const result = checkbox.closest('.search-result-item');
            const title = result.querySelector('h3, .result-title')?.textContent || 'Unknown';
            const url = result.querySelector('a')?.href || '';

            const item = document.createElement('div');
            item.className = 'preview-item';
            item.innerHTML = `
                <div class="preview-title">${title}</div>
                <div class="preview-url">${url}</div>
            `;
            
            item.style.cssText = `
                padding: 10px;
                border: 1px solid #eee;
                border-radius: 4px;
                margin-bottom: 8px;
                background: #f9f9f9;
            `;

            previewContainer.appendChild(item);
        });
    }

    saveCollection(modal) {
        const name = modal.querySelector('#collection-name').value.trim();
        const description = modal.querySelector('#collection-desc').value.trim();
        const privacy = modal.querySelector('#collection-privacy').value;
        const tags = modal.querySelector('#collection-tags').value.split(',').map(tag => tag.trim()).filter(tag => tag);

        if (!name) {
            alert('Please enter a collection name.');
            return;
        }

        // Get selected results or all current results
        const selectedCheckboxes = document.querySelectorAll('.result-checkbox:checked');
        const results = [];

        if (selectedCheckboxes.length > 0) {
            selectedCheckboxes.forEach(checkbox => {
                const result = checkbox.closest('.search-result-item');
                results.push({
                    title: result.querySelector('h3, .result-title')?.textContent || '',
                    url: result.querySelector('a')?.href || '',
                    description: result.querySelector('.result-description, p')?.textContent || ''
                });
            });
        } else {
            // Include all current search results
            document.querySelectorAll('.search-result-item').forEach(result => {
                results.push({
                    title: result.querySelector('h3, .result-title')?.textContent || '',
                    url: result.querySelector('a')?.href || '',
                    description: result.querySelector('.result-description, p')?.textContent || ''
                });
            });
        }

        const collection = {
            id: Date.now(),
            name: name,
            description: description,
            privacy: privacy,
            tags: tags,
            results: results,
            query: new URLSearchParams(window.location.search).get('query') || '',
            created: new Date().toISOString(),
            shared: 0,
            views: 0
        };

        // Save to localStorage
        let collections = JSON.parse(localStorage.getItem('search_collections') || '[]');
        collections.unshift(collection);
        localStorage.setItem('search_collections', JSON.stringify(collections));

        modal.remove();
        this.showToast(`Collection "${name}" created successfully!`);

        // Award points for creating collection
        if (typeof addUserPoints === 'function') {
            addUserPoints(15, 'collection_created', 'Created search collection');
        }
    }

    startCollaboration() {
        // Real-time collaboration feature
        const collaborationId = this.generateCollaborationId();
        const currentUrl = window.location.href;

        const modal = document.createElement('div');
        modal.className = 'collab-modal';
        modal.innerHTML = `
            <div class="collab-modal-content">
                <div class="collab-header">
                    <h3>Collaborative Search</h3>
                    <button class="close-collab">&times;</button>
                </div>
                <div class="collab-body">
                    <div class="collab-info">
                        <p>Start a collaborative search session and invite others to join your search!</p>
                        <div class="collab-id">
                            <label>Session ID:</label>
                            <div class="id-display">
                                <code>${collaborationId}</code>
                                <button class="copy-id">📋</button>
                            </div>
                        </div>
                        <div class="share-link">
                            <label>Share Link:</label>
                            <div class="link-display">
                                <input type="text" value="${currentUrl}&collab=${collaborationId}" readonly>
                                <button class="copy-link">📋</button>
                            </div>
                        </div>
                    </div>
                    <div class="collab-participants">
                        <h4>Participants (1)</h4>
                        <div class="participants-list">
                            <div class="participant">
                                <div class="participant-avatar">👤</div>
                                <div class="participant-info">
                                    <div class="participant-name">You</div>
                                    <div class="participant-status">Host</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="collab-activity">
                        <h4>Activity Feed</h4>
                        <div class="activity-list">
                            <div class="activity-item">
                                <span class="activity-time">${new Date().toLocaleTimeString()}</span>
                                <span class="activity-text">Collaboration session started</span>
                            </div>
                        </div>
                    </div>
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

        document.body.appendChild(modal);
        this.setupCollaborationModal(modal, collaborationId);
    }

    setupCollaborationModal(modal, collaborationId) {
        // Close modal
        modal.querySelector('.close-collab').addEventListener('click', () => {
            modal.remove();
        });

        // Copy ID and link
        modal.querySelector('.copy-id').addEventListener('click', () => {
            navigator.clipboard.writeText(collaborationId);
            this.showToast('Session ID copied!');
        });

        modal.querySelector('.copy-link').addEventListener('click', () => {
            const link = modal.querySelector('.link-display input').value;
            navigator.clipboard.writeText(link);
            this.showToast('Collaboration link copied!');
        });

        // Initialize collaboration session
        this.initializeCollaborationSession(collaborationId, modal);
    }

    generateCollaborationId() {
        return Math.random().toString(36).substr(2, 9).toUpperCase();
    }

    initializeCollaborationSession(collaborationId, modal) {
        // Store collaboration session
        const session = {
            id: collaborationId,
            created: new Date().toISOString(),
            participants: ['You'],
            activity: [`${new Date().toLocaleTimeString()} - Collaboration session started`],
            currentQuery: new URLSearchParams(window.location.search).get('query') || ''
        };

        this.collaborativeSearches.set(collaborationId, session);

        // Award points for starting collaboration
        if (typeof addUserPoints === 'function') {
            addUserPoints(10, 'collab_started', 'Started collaborative search');
        }
    }

    saveToShareHistory(platform, shareData) {
        const shareRecord = {
            platform: platform,
            title: shareData.title,
            url: shareData.url,
            timestamp: new Date().toISOString()
        };

        this.shareHistory.unshift(shareRecord);
        
        // Keep only last 50 shares
        if (this.shareHistory.length > 50) {
            this.shareHistory = this.shareHistory.slice(0, 50);
        }

        localStorage.setItem('share_history', JSON.stringify(this.shareHistory));
    }

    addCollaborationPanel() {
        // Check if we're in a collaborative session
        const urlParams = new URLSearchParams(window.location.search);
        const collaborationId = urlParams.get('collab');

        if (collaborationId) {
            this.joinCollaborationSession(collaborationId);
        }
    }

    joinCollaborationSession(collaborationId) {
        // Create collaboration indicator
        const indicator = document.createElement('div');
        indicator.className = 'collaboration-indicator';
        indicator.innerHTML = `
            <div class="collab-status">
                👥 Collaborative Session: ${collaborationId}
                <button class="leave-collab">Leave</button>
            </div>
        `;

        indicator.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            font-size: 14px;
        `;

        document.body.appendChild(indicator);

        // Setup leave button
        indicator.querySelector('.leave-collab').addEventListener('click', () => {
            const url = new URL(window.location);
            url.searchParams.delete('collab');
            window.location.href = url.toString();
        });

        // Award points for joining collaboration
        if (typeof addUserPoints === 'function') {
            addUserPoints(5, 'collab_joined', 'Joined collaborative search');
        }
    }

    setupEventListeners() {
        // Listen for result selections to update sharing options
        document.addEventListener('change', (e) => {
            if (e.target.matches('.result-checkbox')) {
                this.updateSharingOptions();
            }
        });
    }

    updateSharingOptions() {
        const selectedCount = document.querySelectorAll('.result-checkbox:checked').length;
        const shareBtn = document.querySelector('#share-search');

        if (shareBtn && selectedCount > 0) {
            shareBtn.textContent = `📤 Share Selected (${selectedCount})`;
        } else if (shareBtn) {
            shareBtn.textContent = '📤 Share Search';
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'social-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10000;
            animation: slideInUp 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    initializeCollaboration() {
        // Load share history
        this.shareHistory = JSON.parse(localStorage.getItem('share_history') || '[]');
    }
}

// Initialize social features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.socialFeatures = new SocialFeatures();
});

// Export for use in other modules
window.SocialFeatures = SocialFeatures;