/**
 * Voice Search Module
 * Provides voice search functionality with modern Web Speech API
 */

class VoiceSearch {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isSupported = false;
        this.searchInput = null;
        this.voiceButton = null;
        this.init();
    }

    init() {
        // Check if Web Speech API is supported
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.isSupported = true;
            this.setupRecognition();
        } else {
            console.warn('Web Speech API not supported in this browser');
        }
    }

    setupRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configuration
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'de-DE'; // German by default, can be changed
        this.recognition.maxAlternatives = 1;

        // Event listeners
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.handleResult(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI('error');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI('idle');
        };
    }

    bindToSearchInput(inputElement, buttonElement) {
        this.searchInput = inputElement;
        this.voiceButton = buttonElement;
        
        if (this.isSupported) {
            this.voiceButton.style.display = 'block';
            this.voiceButton.addEventListener('click', () => this.toggleListening());
        } else {
            this.voiceButton.style.display = 'none';
        }
    }

    toggleListening() {
        if (!this.isSupported) return;

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    handleResult(transcript) {
        if (this.searchInput) {
            this.searchInput.value = transcript;
            this.searchInput.dispatchEvent(new Event('input')); // Trigger input event for any listeners
            
            // Add points for voice search
            if (typeof addUserPoints === 'function') {
                addUserPoints(15, 'voice_search', 'Used voice search');
            }
            
            // Auto-submit search if transcript seems complete
            if (transcript.length > 3 && !transcript.endsWith('...')) {
                setTimeout(() => {
                    const form = this.searchInput.closest('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }, 500);
            }
        }
    }

    updateUI(state) {
        if (!this.voiceButton) return;

        const icon = this.voiceButton.querySelector('.voice-icon');
        const ripple = this.voiceButton.querySelector('.voice-ripple');
        
        switch (state) {
            case 'listening':
                icon.textContent = '🎙️';
                this.voiceButton.classList.add('listening');
                this.voiceButton.title = 'Listening... Click to stop';
                if (ripple) ripple.style.display = 'block';
                break;
            case 'error':
                icon.textContent = '🎤';
                this.voiceButton.classList.remove('listening');
                this.voiceButton.classList.add('error');
                this.voiceButton.title = 'Voice search error. Click to try again.';
                if (ripple) ripple.style.display = 'none';
                setTimeout(() => {
                    this.voiceButton.classList.remove('error');
                }, 2000);
                break;
            case 'idle':
            default:
                icon.textContent = '🎤';
                this.voiceButton.classList.remove('listening', 'error');
                this.voiceButton.title = 'Click to start voice search';
                if (ripple) ripple.style.display = 'none';
                break;
        }
    }

    setLanguage(lang) {
        if (this.recognition) {
            this.recognition.lang = lang;
        }
    }
}

// Initialize voice search when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const voiceSearch = new VoiceSearch();
    
    // Bind to main search input
    const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
    const voiceButton = document.querySelector('#voice-search-btn');
    
    if (searchInput && voiceButton) {
        voiceSearch.bindToSearchInput(searchInput, voiceButton);
    }
});

// Export for use in other modules
window.VoiceSearch = VoiceSearch;