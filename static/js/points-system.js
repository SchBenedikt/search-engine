/**
 * User Points System
 * Manages user points, achievements, and gamification features
 */

class PointsSystem {
    constructor() {
        this.userStats = null;
        this.achievementQueue = [];
        this.init();
    }

    init() {
        this.loadUserStats();
        this.setupEventListeners();
        this.createPointsDisplay();
    }

    async loadUserStats() {
        try {
            const response = await fetch('/api/user/stats');
            const data = await response.json();
            
            if (data.success) {
                this.userStats = data.stats;
                this.updatePointsDisplay();
            }
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    async addPoints(points, activityType, description = '') {
        try {
            const response = await fetch('/api/user/add_points', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    points,
                    activity_type: activityType,
                    description
                })
            });

            const data = await response.json();
            
            if (data.success) {
                const oldTotal = this.userStats?.total_points || 0;
                this.userStats.total_points = data.new_total;
                
                // Update level if changed
                const oldLevel = this.userStats?.level || 1;
                await this.loadUserStats(); // Reload to get updated level
                
                // Show points notification
                this.showPointsNotification(points, activityType);
                
                // Check for level up
                if (this.userStats.level > oldLevel) {
                    this.showLevelUpNotification(this.userStats.level);
                }
                
                this.updatePointsDisplay();
                return data.new_total;
            }
        } catch (error) {
            console.error('Error adding points:', error);
        }
        return 0;
    }

    createPointsDisplay() {
        // Create points display in header
        const pointsDisplay = document.createElement('div');
        pointsDisplay.id = 'points-display';
        pointsDisplay.className = 'points-display';
        pointsDisplay.innerHTML = `
            <div class="points-container">
                <div class="points-info">
                    <span class="points-value">0</span>
                    <span class="points-label">Points</span>
                </div>
                <div class="level-info">
                    <span class="level-value">1</span>
                    <span class="level-label">Level</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        `;

        // Add to header
        const header = document.querySelector('.navbar') || document.querySelector('header');
        if (header) {
            header.appendChild(pointsDisplay);
        }

        // Add click handler for detailed stats
        pointsDisplay.addEventListener('click', () => {
            this.showDetailedStats();
        });
    }

    updatePointsDisplay() {
        if (!this.userStats) return;

        const pointsValue = document.querySelector('.points-value');
        const levelValue = document.querySelector('.level-value');
        const progressFill = document.querySelector('.progress-fill');

        if (pointsValue) {
            pointsValue.textContent = this.userStats.total_points;
        }
        
        if (levelValue) {
            levelValue.textContent = this.userStats.level;
        }

        if (progressFill) {
            const progress = this.calculateLevelProgress();
            progressFill.style.width = progress + '%';
        }
    }

    calculateLevelProgress() {
        if (!this.userStats) return 0;
        
        const currentPoints = this.userStats.total_points;
        const currentLevel = this.userStats.level;
        const nextLevelPoints = this.userStats.next_level_points;
        
        // Calculate points needed for current level
        const levelThresholds = [0, 100, 500, 1000, 2500, 5000];
        const currentLevelPoints = levelThresholds[currentLevel - 1] || 0;
        
        const pointsInLevel = currentPoints - currentLevelPoints;
        const pointsNeeded = nextLevelPoints - currentLevelPoints;
        
        return Math.min((pointsInLevel / pointsNeeded) * 100, 100);
    }

    showPointsNotification(points, activityType) {
        const notification = document.createElement('div');
        notification.className = 'points-notification';
        notification.innerHTML = `
            <div class="points-icon">+${points}</div>
            <div class="points-text">${this.getActivityDescription(activityType)}</div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 4000);
    }

    showLevelUpNotification(newLevel) {
        const notification = document.createElement('div');
        notification.className = 'achievement-badge';
        notification.innerHTML = `
            <div class="achievement-icon">🎉</div>
            <h3>Level Up!</h3>
            <p>You've reached level ${newLevel}!</p>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    showDetailedStats() {
        if (!this.userStats) return;

        const modal = document.createElement('div');
        modal.className = 'stats-modal';
        modal.innerHTML = `
            <div class="stats-modal-content">
                <div class="stats-header">
                    <h2>Your Statistics</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${this.userStats.total_points}</div>
                        <div class="stat-label">Total Points</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.userStats.level}</div>
                        <div class="stat-label">Level</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.userStats.searches_count}</div>
                        <div class="stat-label">Searches</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.userStats.ai_queries_count}</div>
                        <div class="stat-label">AI Queries</div>
                    </div>
                </div>
                <div class="achievements-section">
                    <h3>Achievements</h3>
                    <div class="achievements-grid">
                        ${this.renderAchievements()}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal functionality
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    renderAchievements() {
        const achievements = [
            {id: 'first_search', name: 'First Search', description: 'Performed your first search', icon: '🔍'},
            {id: 'search_explorer', name: 'Search Explorer', description: 'Performed 10 searches', icon: '🌟'},
            {id: 'search_master', name: 'Search Master', description: 'Performed 50 searches', icon: '🏆'},
            {id: 'ai_curious', name: 'AI Curious', description: 'Asked your first AI question', icon: '🤖'},
            {id: 'ai_enthusiast', name: 'AI Enthusiast', description: 'Asked 20 AI questions', icon: '🧠'},
            {id: 'point_collector', name: 'Point Collector', description: 'Earned 100 points', icon: '💎'},
            {id: 'level_up', name: 'Level Up', description: 'Reached level 3', icon: '⬆️'},
        ];

        return achievements.map(achievement => {
            const earned = this.userStats.achievements.includes(achievement.id);
            return `
                <div class="achievement-item ${earned ? 'earned' : 'locked'}">
                    <div class="achievement-icon">${achievement.icon}</div>
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                </div>
            `;
        }).join('');
    }

    getActivityDescription(activityType) {
        const descriptions = {
            'search': 'Search performed',
            'ai_query': 'AI question asked',
            'website_chat': 'Website chat',
            'voice_search': 'Voice search used',
            'daily_login': 'Daily visit',
            'feature_discovery': 'Feature discovered'
        };
        return descriptions[activityType] || 'Points earned';
    }

    setupEventListeners() {
        // Listen for search events
        document.addEventListener('search-performed', (e) => {
            this.addPoints(5, 'search', 'Search performed');
        });

        // Listen for AI query events
        document.addEventListener('ai-query-performed', (e) => {
            this.addPoints(10, 'ai_query', 'AI query performed');
        });

        // Listen for voice search events
        document.addEventListener('voice-search-used', (e) => {
            this.addPoints(15, 'voice_search', 'Voice search used');
        });
    }
}

// Global function to add points (used by other modules)
window.addUserPoints = function(points, activityType, description = '') {
    if (window.pointsSystem) {
        return window.pointsSystem.addPoints(points, activityType, description);
    }
    return 0;
};

// Initialize points system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pointsSystem = new PointsSystem();
});

// Export for use in other modules
window.PointsSystem = PointsSystem;