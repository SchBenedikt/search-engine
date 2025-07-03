/**
 * Enhanced Animations and Micro-interactions
 * Provides modern UI animations and user feedback
 */

class AnimationEnhancer {
    constructor() {
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupHoverEffects();
        this.setupClickEffects();
        this.setupScrollAnimations();
        this.setupLoadingAnimations();
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    
                    // Add staggered animation for child elements
                    const children = entry.target.querySelectorAll('.animate-child');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('animate-in');
                        }, index * 100);
                    });
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        // Observe elements with animation classes
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    setupHoverEffects() {
        // Enhanced card hover effects
        document.querySelectorAll('.feature-card, .search-result-item').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px) scale(1.02)';
                card.style.boxShadow = '0 10px 30px rgba(0,0,0,0.15)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            });
        });

        // Button hover effects
        document.querySelectorAll('.btn, .search-button').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px)';
                btn.style.filter = 'brightness(1.1)';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
                btn.style.filter = 'brightness(1)';
            });
        });
    }

    setupClickEffects() {
        // Ripple effect for buttons
        document.querySelectorAll('.btn, .search-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const ripple = document.createElement('div');
                ripple.classList.add('ripple');
                
                const rect = btn.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                btn.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Click feedback for interactive elements
        document.querySelectorAll('.clickable').forEach(el => {
            el.addEventListener('click', () => {
                el.classList.add('clicked');
                setTimeout(() => {
                    el.classList.remove('clicked');
                }, 150);
            });
        });
    }

    setupScrollAnimations() {
        // Smooth scroll to top button
        this.createScrollToTopButton();

        // Parallax effect for header
        const header = document.querySelector('.hero-section');
        if (header) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const parallax = scrolled * 0.5;
                header.style.transform = `translateY(${parallax}px)`;
            });
        }

        // Progress bar during scroll
        this.createScrollProgressBar();
    }

    createScrollToTopButton() {
        const scrollBtn = document.createElement('button');
        scrollBtn.innerHTML = '↑';
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--primary-color, #007bff);
            color: white;
            border: none;
            font-size: 20px;
            cursor: pointer;
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(scrollBtn);

        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollBtn.style.opacity = '1';
                scrollBtn.style.transform = 'translateY(0)';
            } else {
                scrollBtn.style.opacity = '0';
                scrollBtn.style.transform = 'translateY(20px)';
            }
        });

        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    createScrollProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress-bar';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, #007bff, #00d4ff);
            z-index: 10000;
            transition: width 0.1s ease;
        `;

        document.body.appendChild(progressBar);

        window.addEventListener('scroll', () => {
            const scrolled = (window.pageYOffset / (document.body.scrollHeight - window.innerHeight)) * 100;
            progressBar.style.width = Math.min(scrolled, 100) + '%';
        });
    }

    setupLoadingAnimations() {
        // Enhanced loading states
        this.createLoadingSpinner();
        this.setupSkeletonLoading();
    }

    createLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = `
            <div class="spinner-ring">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
            </div>
            <div class="loading-text">Searching...</div>
        `;
        spinner.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10000;
            display: none;
            flex-direction: column;
            align-items: center;
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(spinner);

        // Expose global loading functions
        window.showLoading = () => {
            spinner.style.display = 'flex';
        };

        window.hideLoading = () => {
            spinner.style.display = 'none';
        };
    }

    setupSkeletonLoading() {
        // Create skeleton loading for search results
        const skeletonHTML = `
            <div class="skeleton-item">
                <div class="skeleton-line skeleton-title"></div>
                <div class="skeleton-line skeleton-url"></div>
                <div class="skeleton-line skeleton-description"></div>
                <div class="skeleton-line skeleton-description short"></div>
            </div>
        `;

        // Function to show skeleton loading
        window.showSkeletonLoading = (container) => {
            if (container) {
                container.innerHTML = Array(5).fill(skeletonHTML).join('');
            }
        };
    }

    // Utility functions for animations
    animateCounter(element, target, duration = 1000) {
        const start = 0;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            element.textContent = Math.floor(start + (target - start) * easeOutQuart);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    typeWriter(element, text, speed = 50) {
        let i = 0;
        element.textContent = '';
        
        const type = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        };
        
        type();
    }

    pulseElement(element, duration = 1000) {
        element.style.animation = `pulse ${duration}ms ease-in-out`;
        setTimeout(() => {
            element.style.animation = '';
        }, duration);
    }
}

// Initialize animations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AnimationEnhancer();
});

// Export for use in other modules
window.AnimationEnhancer = AnimationEnhancer;