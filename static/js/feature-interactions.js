/**
 * Feature Interaction Animations
 * Enhanced interactive elements for the landing page
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize feature card hover effects
    initFeatureBadges();
    initFeatureCards();
});

/**
 * Initialize the enhanced feature badges with hover animations
 */
function initFeatureBadges() {
    const featureBadges = document.querySelectorAll('.feature-badge');
    
    featureBadges.forEach(badge => {
        // Create glowing background effect element
        const glowEffect = document.createElement('div');
        glowEffect.classList.add('feature-badge-glow');
        badge.appendChild(glowEffect);
        
        badge.addEventListener('mouseenter', () => {
            badge.classList.add('feature-badge-active');
            
            // Animate the icon
            const icon = badge.querySelector('.feature-badge-icon');
            if (icon) {
                icon.classList.add('feature-icon-pulse');
            }
        });
        
        badge.addEventListener('mouseleave', () => {
            badge.classList.remove('feature-badge-active');
            
            // Remove icon animation
            const icon = badge.querySelector('.feature-badge-icon');
            if (icon) {
                icon.classList.remove('feature-icon-pulse');
            }
        });
    });
}

/**
 * Initialize the 3D hover effect for feature cards
 */
function initFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const angleX = (y - centerY) / 20;
            const angleY = (centerX - x) / 20;
            
            this.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale3d(1.03, 1.03, 1.03)`;
            
            // Dynamic shadow based on mouse position
            const shadowX = (x - centerX) / 10;
            const shadowY = (y - centerY) / 10;
            this.style.boxShadow = `${shadowX}px ${shadowY}px 30px rgba(0, 0, 0, 0.15)`;
            
            // Highlight effect
            const highlight = this.querySelector('.card-highlight');
            if (highlight) {
                const percentX = x / rect.width * 100;
                const percentY = y / rect.height * 100;
                highlight.style.background = `radial-gradient(circle at ${percentX}% ${percentY}%, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 60%)`;
            }
        });
        
        // Reset transform on mouse leave
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.05)';
            
            const highlight = this.querySelector('.card-highlight');
            if (highlight) {
                highlight.style.background = 'none';
            }
        });
        
        // Add highlight layer
        const highlight = document.createElement('div');
        highlight.classList.add('card-highlight');
        card.appendChild(highlight);
    });
}
