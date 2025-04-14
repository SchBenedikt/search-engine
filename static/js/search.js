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
    });
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
    aiResponseContainer.innerHTML = '<div class="alert alert-primary mb-4" ><div class="d-flex align-items-center"><div class="spinner-border spinner-border-sm text-primary me-2" role="status"><span class="visually-hidden">Loading...</span></div><span>Generating AI response...</span></div></div>';
    
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

/**
 * Function to open a chat about the content of a website
 */
function openWebsiteChat(url) {
    const modal = new bootstrap.Modal(document.getElementById('website-chat-modal'));
    modal.show();
    
    // Show loading spinner
    document.getElementById('website-chat-loading').style.display = 'block';
    document.getElementById('website-chat-content').style.display = 'none';
    document.getElementById('website-chat-error').style.display = 'none';
    
    // Set the website URL in a data attribute for later use
    document.getElementById('website-chat-messages').setAttribute('data-url', url);
    
    // Fetch the website content
    fetchWebsiteContent(url);
}

/**
 * Function to fetch website content for AI chat
 */
function fetchWebsiteContent(url) {
    fetch('/fetch-website-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'url': url }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide loading, show chat interface
            document.getElementById('website-chat-loading').style.display = 'none';
            document.getElementById('website-chat-content').style.display = 'block';
            
            // Set modal title with the website name
            document.getElementById('websiteChatModalLabel').textContent = 
                'Chat about: ' + (new URL(url)).hostname;
            
            // Display the extracted content in the content preview panel
            if (data.extracted_content) {
                const contentPreview = document.getElementById('website-content-preview');
                // Truncate content if too long
                const truncatedContent = data.extracted_content.length > 5000 
                    ? data.extracted_content.substring(0, 5000) + '...' 
                    : data.extracted_content;
                
                // Format the content
                contentPreview.innerHTML = `<pre>${escapeHtml(truncatedContent)}</pre>`;
            }
                
            // Initialize the chat
            initializeWebsiteChat(url);
        } else {
            // Show error message
            document.getElementById('website-chat-loading').style.display = 'none';
            document.getElementById('website-chat-error').style.display = 'block';
            document.getElementById('website-chat-error').textContent = 
                'Der Websiteinhalt konnte nicht geladen werden: ' + data.error;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('website-chat-loading').style.display = 'none';
        document.getElementById('website-chat-error').style.display = 'block';
    });
}

/**
 * Function to initialize the website chat interface
 */
function initializeWebsiteChat(url) {
    // Clear previous messages except the first one (AI greeting)
    const chatMessages = document.getElementById('website-chat-messages');
    while (chatMessages.children.length > 1) {
        chatMessages.removeChild(chatMessages.lastChild);
    }
    
    // Set up the send button event
    const sendButton = document.getElementById('website-chat-send');
    const chatInput = document.getElementById('website-chat-input');
    
    // Remove previous event listeners
    sendButton.replaceWith(sendButton.cloneNode(true));
    
    // Get the new button and add event listener
    const newSendButton = document.getElementById('website-chat-send');
    newSendButton.addEventListener('click', sendWebsiteChatMessage);
    
    // Add event listener for pressing Enter in the input field
    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendWebsiteChatMessage();
        }
    });
    
    // Scroll to bottom if needed
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Function to send a message in the website chat
 */
function sendWebsiteChatMessage() {
    const chatInput = document.getElementById('website-chat-input');
    const message = chatInput.value.trim();
    
    if (message === '') {
        return;
    }
    
    const chatMessages = document.getElementById('website-chat-messages');
    const url = chatMessages.getAttribute('data-url');
    
    // Add user message to the chat
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'user-message';
    userMessageDiv.innerHTML = `<p>${escapeHtml(message)}</p>`;
    chatMessages.appendChild(userMessageDiv);
    
    // Clear input
    chatInput.value = '';
    
    // Add loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-message-loading';
    loadingDiv.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
        <span>Thinking...</span>
    `;
    chatMessages.appendChild(loadingDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Send message to server
    fetch('/chat-with-website', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            'url': url,
            'message': message 
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading message
        chatMessages.removeChild(loadingDiv);
        
        if (data.success) {
            // Add AI response
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'ai-message';
            aiMessageDiv.innerHTML = `<p>${formatAIResponse(data.response)}</p>`;
            chatMessages.appendChild(aiMessageDiv);
        } else {
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'ai-message error';
            errorDiv.innerHTML = `<p>Es ist ein Fehler aufgetreten: ${data.error}</p>`;
            chatMessages.appendChild(errorDiv);
        }
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Remove loading message
        chatMessages.removeChild(loadingDiv);
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'ai-message error';
        errorDiv.innerHTML = '<p>Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.</p>';
        chatMessages.appendChild(errorDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

/**
 * Helper function to escape HTML
 */
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Helper function to format AI responses with markdown support
 */
function formatAIResponse(text) {
    return marked.parse(text);
}


