/**
 * Preview tooltip functionality for search results
 */

$(document).ready(function () {
    // Variables for cursor-following preview
    let hoverTimeout;
    let activePreview = null;
    const hoverDelay = 500; // Delay in ms before loading the summary
    const offsetX = 15; // Offset from cursor X position
    const offsetY = 15; // Offset from cursor Y position
    
    // Create a single tooltip element for the entire page
    const globalTooltip = $('<div class="preview-tooltip">' +
        '<div class="preview-loading">' +
        '<div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>' +
        '<span>Loading preview...</span>' +
        '</div>' +
        '<div class="preview-content" style="display: none;"></div>' +
        '<div class="preview-error" style="display: none;">Preview could not be loaded</div>' +
        '</div>');
    
    $('body').append(globalTooltip);
    
    // Track mouse movement when hovering over result items
    $(document).on('mousemove', function(e) {
        if (activePreview) {
            // Position the tooltip near the cursor - using clientX/Y for viewport-relative positioning
            const windowWidth = $(window).width();
            const windowHeight = $(window).height(); 
            const tooltipWidth = globalTooltip.outerWidth();
            const tooltipHeight = globalTooltip.outerHeight();
            
            // Calculate position based on client coordinates (viewport-relative)
            // This ensures proper positioning regardless of scroll position
            let leftPos, topPos;
            
            // Horizontal positioning
            if (e.clientX + tooltipWidth + offsetX > windowWidth) {
                // Show tooltip to the left of cursor if it would overflow right edge
                leftPos = e.clientX - tooltipWidth - offsetX;
            } else {
                // Show tooltip to the right of cursor
                leftPos = e.clientX + offsetX;
            }
            
            // Vertical positioning
            if (e.clientY > windowHeight / 2) {
                // Show above cursor if in lower half of viewport
                topPos = e.clientY - tooltipHeight - 10;
            } else {
                // Show below cursor if in upper half of viewport
                topPos = e.clientY + offsetY;
            }
            
            // Make sure tooltip stays within viewport
            if (topPos < 0) {
                topPos = offsetY;
            } else if (topPos + tooltipHeight > windowHeight) {
                topPos = windowHeight - tooltipHeight - 10;
            }
            
            if (leftPos < 0) {
                leftPos = offsetX;
            }
            
            // Apply fixed positioning with viewport coordinates
            globalTooltip.css({
                left: leftPos + 'px',
                top: topPos + 'px'
            });
        }
    });
    
    // Add hover handlers to result items
    $('.result-item').hover(
        function(e) {
            const resultItem = $(this);
            const url = resultItem.data('url');
            
            const previewLoading = globalTooltip.find('.preview-loading');
            const previewContent = globalTooltip.find('.preview-content');
            const previewError = globalTooltip.find('.preview-error');
            
            // Store current result item as active
            activePreview = resultItem;
            
            // Position tooltip initially - with improved positioning logic
            const windowWidth = $(window).width();
            const windowHeight = $(window).height();
            const tooltipWidth = globalTooltip.outerWidth();
            const scrollTop = $(window).scrollTop();
            
            // Determine initial position - above or below cursor based on position
            let topPos;
            if (e.clientY > windowHeight / 2) {
                // Show above cursor if in lower half of screen
                topPos = e.pageY - 300 - 10; // Estimate height initially
            } else {
                // Show below cursor if in upper half of screen
                topPos = e.pageY + offsetY;
            }
            
            // Make sure tooltip stays within window bounds
            let leftPos = e.pageX + offsetX;
            if (leftPos + tooltipWidth > windowWidth - 20) {
                leftPos = e.pageX - tooltipWidth - offsetX;
            }
            
            globalTooltip.css({
                left: leftPos + 'px',
                top: topPos + 'px'
            });
            
            // Set timeout to prevent loading on brief hovers
            hoverTimeout = setTimeout(function() {
                // Mark the preview as active (visible)
                globalTooltip.addClass('active');
                
                // Check if we already have content for this URL
                const cachedContent = resultItem.data('preview-content');
                if (cachedContent) {
                    previewLoading.hide();
                    previewError.hide();
                    previewContent.html(cachedContent);
                    previewContent.show();
                    return;
                }
                
                // Show loading state
                previewLoading.show();
                previewContent.hide();
                previewError.hide();
                
                // Fetch summary from the server
                fetch(`/get_page_summary?url=${encodeURIComponent(url)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.summary) {
                            // Convert Markdown to HTML
                            let summary = data.summary;
                            
                            // Process source references in square brackets [n]
                            summary = summary.replace(/\[(\d+)\]/g, function(match, number) {
                                if (data.sources && data.sources[number-1]) {
                                    const source = data.sources[number-1];
                                    return `<a href="${source.uri}" target="_blank" class="source-link">[${number}]</a>`;
                                }
                                return match;
                            });
                            
                            // Use marked.js for Markdown conversion
                            const renderedHTML = marked.parse(summary);
                            previewContent.html(renderedHTML);
                            previewContent.addClass('markdown-body');
                            
                            // Cache the content for this URL
                            resultItem.data('preview-content', renderedHTML);
                            
                            previewLoading.hide();
                            previewContent.show();
                        } else {
                            previewLoading.hide();
                            previewError.show();
                        }
                    })
                    .catch(err => {
                        console.error('Summary loading error:', err);
                        previewLoading.hide();
                        previewError.show();
                    });
            }, hoverDelay);
        },
        function() {
            // On mouse out, clear the timeout and hide tooltip
            clearTimeout(hoverTimeout);
            globalTooltip.removeClass('active');
            activePreview = null;
        }
    );
});
