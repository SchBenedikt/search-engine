/**
 * Main JavaScript for search page functionality
 */

document.addEventListener('DOMContentLoaded', function () {
    // Show search time toast
    var toastEl = document.getElementById('search-time-toast');
    if (toastEl) {
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    // Load favicons asynchronously
    loadFavicons();
    
    // If AI response URL is provided, load it
    initializeAIResponse();
});

/**
 * Function to handle liking search results
 */
function likeResult(url) {
    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'url': url }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var successToast = new bootstrap.Toast(document.getElementById('success-like-toast'));
            successToast.show();
        } else {
            var errorToast = new bootstrap.Toast(document.getElementById('like-error'));
            errorToast.show();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred.');
}

/**
 * Function to toggle between short and full AI responses
 */
function toggleAIResponse(button) {
    const container = button.closest('.ai-response');
    const preview = container.querySelector('.ai-response-preview');
    const full = container.querySelector('.ai-response-full');
    
    if (preview.style.display !== 'none') {
        // Switch to full response
        preview.style.display = 'none';
        full.style.display = 'block';
        button.textContent = 'Show less';
    } else {
        // Switch to preview
        preview.style.display = 'block';
        full.style.display = 'none';
        button.textContent = 'Show more';
    }
}

/**
 * Load favicons asynchronously
 */
function loadFavicons() {
    document.querySelectorAll('img.fav-icon').forEach(function(img) {
        const url = img.getAttribute('data-url');
        fetch('/favicon?url=' + encodeURIComponent(url))
            .then(response => response.json())
            .then(data => {
                if (data.favicon) {
                    img.src = data.favicon;
                    img.style.display = 'inline-block';
                }
            })
            .catch(err => console.error('Favicon load error:', err));
    });
}

/**
 * Initialize AI response if available
 */
function initializeAIResponse() {
    const aiResponseUrlElement = document.getElementById('ai-response-url');
    if (!aiResponseUrlElement) return;
    
    const aiResponseUrl = aiResponseUrlElement.getAttribute('data-url');
    if (!aiResponseUrl) return;

    const aiResponseContainer = document.getElementById('ai-response-container');
    aiResponseContainer.innerHTML = '<div class="alert alert-light mb-4"><div class="d-flex align-items-center"><div class="spinner-border spinner-border-sm text-primary me-2" role="status"><span class="visually-hidden">Loading...</span></div><span>Generating AI response...</span></div></div>';
    
    // Fetch the AI response after page load
    fetch(aiResponseUrl)
        .then(response => response.json())
        .then(data => {
            if (data.ai_response_html) {
                aiResponseContainer.innerHTML = data.ai_response_html;
                // After inserting the HTML, process any markdown content
                renderMarkdown();
            } else {
                aiResponseContainer.innerHTML = '';
            }
        })
        .catch(err => {
            console.error('AI response loading error:', err);
            aiResponseContainer.innerHTML = '<div class="alert alert-danger mb-4">Error loading AI response. Please try again.</div>';
        });
}

/**
 * Render markdown content in the page
 */
function renderMarkdown() {
    // Find all markdown content containers
    document.querySelectorAll('.markdown-body').forEach(function(element) {
        // Get the raw text content
        const markdownContent = element.textContent;
        // Render the markdown to HTML using the marked library
        element.innerHTML = marked.parse(markdownContent);
    });
}
