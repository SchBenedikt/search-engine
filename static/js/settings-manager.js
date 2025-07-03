/**
 * Settings Panel and Configuration Management
 * Comprehensive settings interface for all search engine features
 */

class SettingsManager {
    constructor() {
        this.settings = {
            // Search preferences
            resultsPerPage: 10,
            defaultLanguage: 'en',
            safeSearch: 'moderate',
            instantSearch: true,
            searchSuggestions: true,
            
            // Voice search
            voiceLanguage: 'en-US',
            voiceAutoSubmit: true,
            
            // Appearance
            theme: 'auto', // light, dark, auto
            animationsEnabled: true,
            compactMode: false,
            
            // Privacy
            saveSearchHistory: true,
            personalizedResults: true,
            analyticsOptOut: false,
            
            // Notifications
            achievementNotifications: true,
            collaborationNotifications: true,
            
            // Advanced
            advancedMode: false,
            experimentalFeatures: false,
            apiTimeout: 30
        };
        
        this.init();
    }

    init() {
        this.loadSettings();
        this.createSettingsButton();
        this.setupThemeDetection();
        this.applyCurrentSettings();
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('search_engine_settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
    }

    saveSettings() {
        localStorage.setItem('search_engine_settings', JSON.stringify(this.settings));
        this.applyCurrentSettings();
    }

    createSettingsButton() {
        // Add settings button to header/navigation
        const nav = document.querySelector('.navbar, nav, header');
        if (nav && !nav.querySelector('.settings-trigger')) {
            const settingsBtn = document.createElement('button');
            settingsBtn.className = 'settings-trigger';
            settingsBtn.innerHTML = '⚙️';
            settingsBtn.title = 'Settings';
            settingsBtn.style.cssText = `
                position: fixed;
                top: 60px;
                right: 10px;
                background: rgba(255,255,255,0.9);
                border: 1px solid #ddd;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                cursor: pointer;
                font-size: 16px;
                z-index: 999;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            `;

            settingsBtn.addEventListener('mouseenter', () => {
                settingsBtn.style.transform = 'scale(1.1)';
                settingsBtn.style.background = 'white';
            });

            settingsBtn.addEventListener('mouseleave', () => {
                settingsBtn.style.transform = 'scale(1)';
                settingsBtn.style.background = 'rgba(255,255,255,0.9)';
            });

            settingsBtn.addEventListener('click', () => {
                this.openSettingsPanel();
            });

            document.body.appendChild(settingsBtn);
        }
    }

    openSettingsPanel() {
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.innerHTML = this.createSettingsHTML();

        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        `;

        document.body.appendChild(modal);
        this.setupSettingsPanel(modal);
    }

    createSettingsHTML() {
        return `
            <div class="settings-panel">
                <div class="settings-header">
                    <h2>Settings</h2>
                    <button class="close-settings">&times;</button>
                </div>
                <div class="settings-content">
                    <div class="settings-sidebar">
                        <div class="settings-tabs">
                            <button class="tab-btn active" data-tab="general">
                                🔧 General
                            </button>
                            <button class="tab-btn" data-tab="search">
                                🔍 Search
                            </button>
                            <button class="tab-btn" data-tab="appearance">
                                🎨 Appearance
                            </button>
                            <button class="tab-btn" data-tab="privacy">
                                🔒 Privacy
                            </button>
                            <button class="tab-btn" data-tab="notifications">
                                🔔 Notifications
                            </button>
                            <button class="tab-btn" data-tab="advanced">
                                ⚡ Advanced
                            </button>
                            <button class="tab-btn" data-tab="data">
                                💾 Data Management
                            </button>
                            <button class="tab-btn" data-tab="about">
                                ℹ️ About
                            </button>
                        </div>
                    </div>
                    <div class="settings-main">
                        ${this.createTabContent()}
                    </div>
                </div>
                <div class="settings-footer">
                    <button class="btn-reset">Reset to Defaults</button>
                    <div class="footer-actions">
                        <button class="btn-cancel">Cancel</button>
                        <button class="btn-save">Save Changes</button>
                    </div>
                </div>
            </div>
        `;
    }

    createTabContent() {
        return `
            <!-- General Tab -->
            <div class="tab-content active" data-tab="general">
                <h3>General Settings</h3>
                <div class="setting-group">
                    <label>Results per page:</label>
                    <select id="resultsPerPage">
                        <option value="5">5 results</option>
                        <option value="10">10 results</option>
                        <option value="20">20 results</option>
                        <option value="50">50 results</option>
                    </select>
                </div>
                <div class="setting-group">
                    <label>Default language:</label>
                    <select id="defaultLanguage">
                        <option value="en">English</option>
                        <option value="de">German</option>
                        <option value="fr">French</option>
                        <option value="es">Spanish</option>
                        <option value="it">Italian</option>
                    </select>
                </div>
                <div class="setting-group">
                    <label>Safe search:</label>
                    <select id="safeSearch">
                        <option value="off">Off</option>
                        <option value="moderate">Moderate</option>
                        <option value="strict">Strict</option>
                    </select>
                </div>
            </div>

            <!-- Search Tab -->
            <div class="tab-content" data-tab="search">
                <h3>Search Preferences</h3>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="instantSearch">
                        <span>Enable instant search</span>
                        <small>Show results as you type</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="searchSuggestions">
                        <span>Search suggestions</span>
                        <small>Show search history and trending queries</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label>Voice search language:</label>
                    <select id="voiceLanguage">
                        <option value="en-US">English (US)</option>
                        <option value="en-GB">English (UK)</option>
                        <option value="de-DE">German</option>
                        <option value="fr-FR">French</option>
                        <option value="es-ES">Spanish</option>
                    </select>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="voiceAutoSubmit">
                        <span>Auto-submit voice searches</span>
                        <small>Automatically search after voice input</small>
                    </label>
                </div>
            </div>

            <!-- Appearance Tab -->
            <div class="tab-content" data-tab="appearance">
                <h3>Appearance</h3>
                <div class="setting-group">
                    <label>Theme:</label>
                    <div class="theme-options">
                        <label class="radio-label">
                            <input type="radio" name="theme" value="light">
                            <span>☀️ Light</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="theme" value="dark">
                            <span>🌙 Dark</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="theme" value="auto">
                            <span>🔄 Auto</span>
                        </label>
                    </div>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="animationsEnabled">
                        <span>Enable animations</span>
                        <small>Show smooth transitions and effects</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="compactMode">
                        <span>Compact mode</span>
                        <small>Show more results in less space</small>
                    </label>
                </div>
            </div>

            <!-- Privacy Tab -->
            <div class="tab-content" data-tab="privacy">
                <h3>Privacy & Data</h3>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="saveSearchHistory">
                        <span>Save search history</span>
                        <small>Store your searches for suggestions and history</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="personalizedResults">
                        <span>Personalized results</span>
                        <small>Use your search history to improve results</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="analyticsOptOut">
                        <span>Opt out of analytics</span>
                        <small>Don't send usage data for improvement</small>
                    </label>
                </div>
            </div>

            <!-- Notifications Tab -->
            <div class="tab-content" data-tab="notifications">
                <h3>Notifications</h3>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="achievementNotifications">
                        <span>Achievement notifications</span>
                        <small>Show when you earn points and achievements</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="collaborationNotifications">
                        <span>Collaboration notifications</span>
                        <small>Notify when someone joins your collaborative search</small>
                    </label>
                </div>
            </div>

            <!-- Advanced Tab -->
            <div class="tab-content" data-tab="advanced">
                <h3>Advanced Settings</h3>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="advancedMode">
                        <span>Advanced mode</span>
                        <small>Show additional search options and filters</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="experimentalFeatures">
                        <span>Experimental features</span>
                        <small>Enable beta features (may be unstable)</small>
                    </label>
                </div>
                <div class="setting-group">
                    <label>API timeout (seconds):</label>
                    <input type="number" id="apiTimeout" min="5" max="120" value="30">
                </div>
            </div>

            <!-- Data Management Tab -->
            <div class="tab-content" data-tab="data">
                <h3>Data Management</h3>
                <div class="data-section">
                    <h4>Search History</h4>
                    <div class="data-actions">
                        <button class="data-btn" id="exportHistory">📥 Export History</button>
                        <button class="data-btn" id="importHistory">📤 Import History</button>
                        <button class="data-btn danger" id="clearHistory">🗑️ Clear History</button>
                    </div>
                </div>
                <div class="data-section">
                    <h4>Favorites & Collections</h4>
                    <div class="data-actions">
                        <button class="data-btn" id="exportCollections">📥 Export Collections</button>
                        <button class="data-btn danger" id="clearCollections">🗑️ Clear Collections</button>
                    </div>
                </div>
                <div class="data-section">
                    <h4>User Data</h4>
                    <div class="data-actions">
                        <button class="data-btn" id="exportAllData">📦 Export All Data</button>
                        <button class="data-btn danger" id="resetAllData">⚠️ Reset Everything</button>
                    </div>
                </div>
            </div>

            <!-- About Tab -->
            <div class="tab-content" data-tab="about">
                <h3>About iSearch</h3>
                <div class="about-content">
                    <div class="app-info">
                        <h4>🚀 iSearch - Modern AI-Powered Search Engine</h4>
                        <p>Version 2.0.0</p>
                        <p>A next-generation search engine with deep AI integration, gamification, and collaborative features.</p>
                    </div>
                    <div class="features-overview">
                        <h4>✨ Key Features</h4>
                        <ul>
                            <li>🤖 AI-powered search results and answers</li>
                            <li>🎤 Voice search with multi-language support</li>
                            <li>🏆 Gamification with points and achievements</li>
                            <li>👥 Collaborative search sessions</li>
                            <li>📚 Search collections and favorites</li>
                            <li>🔍 Advanced search filters and options</li>
                            <li>📱 Responsive design for all devices</li>
                            <li>🌙 Dark mode and accessibility features</li>
                        </ul>
                    </div>
                    <div class="credits">
                        <h4>🙏 Credits</h4>
                        <p>Built with modern web technologies and powered by Google's Gemini AI.</p>
                        <div class="tech-stack">
                            <span class="tech-badge">Flask</span>
                            <span class="tech-badge">JavaScript</span>
                            <span class="tech-badge">MongoDB</span>
                            <span class="tech-badge">Google Gemini</span>
                            <span class="tech-badge">Web Speech API</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupSettingsPanel(modal) {
        // Add CSS for settings panel
        this.addSettingsCSS();

        // Load current values
        this.loadCurrentValues(modal);

        // Tab switching
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(modal, btn.dataset.tab);
            });
        });

        // Close modal
        modal.querySelector('.close-settings').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelector('.btn-cancel').addEventListener('click', () => {
            modal.remove();
        });

        // Save settings
        modal.querySelector('.btn-save').addEventListener('click', () => {
            this.saveSettingsFromPanel(modal);
            modal.remove();
        });

        // Reset settings
        modal.querySelector('.btn-reset').addEventListener('click', () => {
            if (confirm('Reset all settings to defaults? This cannot be undone.')) {
                this.resetToDefaults();
                modal.remove();
            }
        });

        // Data management actions
        this.setupDataManagement(modal);

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    addSettingsCSS() {
        if (document.querySelector('#settings-styles')) return;

        const style = document.createElement('style');
        style.id = 'settings-styles';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .settings-panel {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 900px;
                height: 80vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }

            .settings-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 25px;
                border-bottom: 1px solid #eee;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .settings-header h2 {
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }

            .close-settings {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 5px 10px;
                border-radius: 4px;
                transition: background 0.2s ease;
            }

            .close-settings:hover {
                background: rgba(255,255,255,0.3);
            }

            .settings-content {
                flex: 1;
                display: flex;
                overflow: hidden;
            }

            .settings-sidebar {
                width: 200px;
                background: #f8f9fa;
                border-right: 1px solid #eee;
                overflow-y: auto;
            }

            .settings-tabs {
                padding: 0;
            }

            .tab-btn {
                width: 100%;
                padding: 15px 20px;
                border: none;
                background: none;
                text-align: left;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s ease;
                border-bottom: 1px solid #eee;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .tab-btn:hover {
                background: #e9ecef;
            }

            .tab-btn.active {
                background: #007bff;
                color: white;
            }

            .settings-main {
                flex: 1;
                overflow-y: auto;
                padding: 25px;
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
            }

            .tab-content h3 {
                margin: 0 0 25px 0;
                font-size: 20px;
                color: #333;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }

            .setting-group {
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid #f0f0f0;
            }

            .setting-group:last-child {
                border-bottom: none;
            }

            .setting-group label {
                display: block;
                font-weight: 500;
                margin-bottom: 8px;
                color: #333;
            }

            .setting-group select,
            .setting-group input[type="number"] {
                width: 100%;
                max-width: 300px;
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }

            .checkbox-label {
                display: flex !important;
                align-items: flex-start;
                gap: 10px;
                cursor: pointer;
                margin-bottom: 0 !important;
            }

            .checkbox-label input[type="checkbox"] {
                margin-top: 2px;
            }

            .checkbox-label span {
                font-weight: 500;
                color: #333;
            }

            .checkbox-label small {
                display: block;
                color: #666;
                font-weight: normal;
                margin-top: 2px;
            }

            .radio-label {
                display: flex !important;
                align-items: center;
                gap: 8px;
                margin-bottom: 10px !important;
                cursor: pointer;
            }

            .theme-options {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .settings-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 25px;
                border-top: 1px solid #eee;
                background: #f8f9fa;
            }

            .footer-actions {
                display: flex;
                gap: 10px;
            }

            .btn-reset,
            .btn-cancel,
            .btn-save {
                padding: 8px 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s ease;
            }

            .btn-reset {
                background: #dc3545;
                color: white;
                border-color: #dc3545;
            }

            .btn-reset:hover {
                background: #c82333;
            }

            .btn-cancel {
                background: white;
                color: #666;
            }

            .btn-cancel:hover {
                background: #f8f9fa;
            }

            .btn-save {
                background: #28a745;
                color: white;
                border-color: #28a745;
            }

            .btn-save:hover {
                background: #218838;
            }

            .data-section {
                margin-bottom: 25px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
            }

            .data-section h4 {
                margin: 0 0 15px 0;
                color: #333;
            }

            .data-actions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .data-btn {
                padding: 6px 12px;
                border: 1px solid #007bff;
                background: white;
                color: #007bff;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s ease;
            }

            .data-btn:hover {
                background: #007bff;
                color: white;
            }

            .data-btn.danger {
                border-color: #dc3545;
                color: #dc3545;
            }

            .data-btn.danger:hover {
                background: #dc3545;
                color: white;
            }

            .about-content {
                max-width: 600px;
            }

            .app-info,
            .features-overview,
            .credits {
                margin-bottom: 30px;
            }

            .features-overview ul {
                list-style: none;
                padding: 0;
            }

            .features-overview li {
                padding: 5px 0;
                color: #555;
            }

            .tech-stack {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin-top: 10px;
            }

            .tech-badge {
                background: #007bff;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            @media (max-width: 768px) {
                .settings-panel {
                    width: 95%;
                    height: 90vh;
                }

                .settings-content {
                    flex-direction: column;
                }

                .settings-sidebar {
                    width: 100%;
                    max-height: 120px;
                    overflow-x: auto;
                }

                .settings-tabs {
                    display: flex;
                    white-space: nowrap;
                }

                .tab-btn {
                    flex-shrink: 0;
                    border-bottom: none;
                    border-right: 1px solid #eee;
                }

                .settings-main {
                    padding: 15px;
                }

                .data-actions {
                    flex-direction: column;
                }

                .data-btn {
                    width: 100%;
                }
            }
        `;

        document.head.appendChild(style);
    }

    switchTab(modal, tabName) {
        // Update tab buttons
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        modal.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.tab === tabName);
        });
    }

    loadCurrentValues(modal) {
        // Load current settings into form elements
        Object.keys(this.settings).forEach(key => {
            const element = modal.querySelector(`#${key}`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = this.settings[key];
                } else if (element.type === 'radio') {
                    const radio = modal.querySelector(`input[name="${key}"][value="${this.settings[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    element.value = this.settings[key];
                }
            }
        });

        // Handle theme radio buttons
        const themeRadio = modal.querySelector(`input[name="theme"][value="${this.settings.theme}"]`);
        if (themeRadio) themeRadio.checked = true;
    }

    saveSettingsFromPanel(modal) {
        // Save settings from form elements
        Object.keys(this.settings).forEach(key => {
            const element = modal.querySelector(`#${key}`);
            if (element) {
                if (element.type === 'checkbox') {
                    this.settings[key] = element.checked;
                } else if (element.type === 'number') {
                    this.settings[key] = parseInt(element.value);
                } else {
                    this.settings[key] = element.value;
                }
            }
        });

        // Handle theme radio buttons
        const checkedTheme = modal.querySelector('input[name="theme"]:checked');
        if (checkedTheme) {
            this.settings.theme = checkedTheme.value;
        }

        this.saveSettings();
        this.showToast('Settings saved successfully!');

        // Award points for customizing settings
        if (typeof addUserPoints === 'function') {
            addUserPoints(5, 'settings_customized', 'Customized search settings');
        }
    }

    setupDataManagement(modal) {
        // Export history
        modal.querySelector('#exportHistory').addEventListener('click', () => {
            if (window.searchHistory) {
                window.searchHistory.exportHistory();
            }
        });

        // Import history
        modal.querySelector('#importHistory').addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file && window.searchHistory) {
                    window.searchHistory.importHistory(file);
                }
            };
            input.click();
        });

        // Clear history
        modal.querySelector('#clearHistory').addEventListener('click', () => {
            if (window.searchHistory) {
                window.searchHistory.clearHistory();
            }
        });

        // Export collections
        modal.querySelector('#exportCollections').addEventListener('click', () => {
            const collections = JSON.parse(localStorage.getItem('search_collections') || '[]');
            const blob = new Blob([JSON.stringify(collections, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `search-collections-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
        });

        // Clear collections
        modal.querySelector('#clearCollections').addEventListener('click', () => {
            if (confirm('Clear all search collections? This cannot be undone.')) {
                localStorage.removeItem('search_collections');
                this.showToast('Collections cleared successfully!');
            }
        });

        // Export all data
        modal.querySelector('#exportAllData').addEventListener('click', () => {
            this.exportAllUserData();
        });

        // Reset all data
        modal.querySelector('#resetAllData').addEventListener('click', () => {
            if (confirm('Reset ALL data including history, collections, and settings? This cannot be undone.')) {
                this.resetAllUserData();
                modal.remove();
            }
        });
    }

    exportAllUserData() {
        const data = {
            settings: this.settings,
            searchHistory: JSON.parse(localStorage.getItem('search_history') || '[]'),
            favorites: JSON.parse(localStorage.getItem('search_favorites') || '[]'),
            collections: JSON.parse(localStorage.getItem('search_collections') || '[]'),
            savedResults: JSON.parse(localStorage.getItem('saved_results') || '[]'),
            shareHistory: JSON.parse(localStorage.getItem('share_history') || '[]'),
            userProfile: JSON.parse(localStorage.getItem('user_profile') || '{}'),
            exportDate: new Date().toISOString(),
            version: '2.0.0'
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `isearch-complete-backup-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        this.showToast('Complete data export created!');
    }

    resetAllUserData() {
        // Clear all localStorage data
        const keysToRemove = [
            'search_history',
            'search_favorites',
            'search_collections',
            'saved_results',
            'share_history',
            'user_profile',
            'search_engine_settings',
            'search_filters'
        ];

        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
        });

        // Reset settings to defaults
        this.settings = {
            resultsPerPage: 10,
            defaultLanguage: 'en',
            safeSearch: 'moderate',
            instantSearch: true,
            searchSuggestions: true,
            voiceLanguage: 'en-US',
            voiceAutoSubmit: true,
            theme: 'auto',
            animationsEnabled: true,
            compactMode: false,
            saveSearchHistory: true,
            personalizedResults: true,
            analyticsOptOut: false,
            achievementNotifications: true,
            collaborationNotifications: true,
            advancedMode: false,
            experimentalFeatures: false,
            apiTimeout: 30
        };

        this.saveSettings();
        this.showToast('All data reset successfully! Page will reload.');
        
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    resetToDefaults() {
        this.settings = {
            resultsPerPage: 10,
            defaultLanguage: 'en',
            safeSearch: 'moderate',
            instantSearch: true,
            searchSuggestions: true,
            voiceLanguage: 'en-US',
            voiceAutoSubmit: true,
            theme: 'auto',
            animationsEnabled: true,
            compactMode: false,
            saveSearchHistory: true,
            personalizedResults: true,
            analyticsOptOut: false,
            achievementNotifications: true,
            collaborationNotifications: true,
            advancedMode: false,
            experimentalFeatures: false,
            apiTimeout: 30
        };

        this.saveSettings();
        this.showToast('Settings reset to defaults!');
    }

    applyCurrentSettings() {
        // Apply theme
        this.applyTheme();
        
        // Apply animations
        this.applyAnimations();
        
        // Apply compact mode
        this.applyCompactMode();
        
        // Update voice search language
        if (window.VoiceSearch && window.voiceSearch) {
            window.voiceSearch.setLanguage(this.settings.voiceLanguage);
        }
    }

    applyTheme() {
        const body = document.body;
        
        if (this.settings.theme === 'dark') {
            body.classList.add('dark-theme');
            body.classList.remove('light-theme');
        } else if (this.settings.theme === 'light') {
            body.classList.add('light-theme');
            body.classList.remove('dark-theme');
        } else {
            // Auto theme
            body.classList.remove('dark-theme', 'light-theme');
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                body.classList.add('dark-theme');
            } else {
                body.classList.add('light-theme');
            }
        }
    }

    applyAnimations() {
        const body = document.body;
        
        if (this.settings.animationsEnabled) {
            body.classList.remove('no-animations');
        } else {
            body.classList.add('no-animations');
        }
    }

    applyCompactMode() {
        const body = document.body;
        
        if (this.settings.compactMode) {
            body.classList.add('compact-mode');
        } else {
            body.classList.remove('compact-mode');
        }
    }

    setupThemeDetection() {
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (this.settings.theme === 'auto') {
                this.applyTheme();
            }
        });
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'settings-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10002;
            animation: slideInUp 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Public API for accessing settings
    getSetting(key) {
        return this.settings[key];
    }

    setSetting(key, value) {
        this.settings[key] = value;
        this.saveSettings();
    }
}

// Initialize settings when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

// Export for use in other modules
window.SettingsManager = SettingsManager;