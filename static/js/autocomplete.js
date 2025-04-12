/**
 * Autocomplete functionality for search input
 */

$(document).ready(function () {
    // Initialize jQuery UI autocomplete
    $('#search-input').autocomplete({
        source: function (request, response) {
            $.ajax({
                url: '/autocomplete',
                dataType: 'json',
                data: {
                    term: request.term
                },
                success: function (data) {
                    response(data);
                }
            });
        },
        minLength: 2, // Minimum length to trigger autocomplete
        select: function (event, ui) {
            // When a suggestion is selected, check if it's a single result
            $.ajax({
                url: '/check_single_result',
                dataType: 'json',
                data: {
                    term: ui.item.value
                },
                success: function (data) {
                    if (data.has_single_result) {
                        // Open page in new tab
                        window.open(data.single_result_url, '_blank');
                    } else {
                        // Submit search form with selected suggestion
                        $('#search-input').val(ui.item.value);
                        $('#search-input').closest('form').submit();
                    }
                }
            });
        }
    });
});
