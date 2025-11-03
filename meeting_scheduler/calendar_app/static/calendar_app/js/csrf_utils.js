/**
 * CSRF Utilities for Django
 *
 * Provides functions for retrieving and handling Django's CSRF tokens
 * in AJAX requests and form submissions.
 *
 * @module csrf_utils
 */

/**
 * Get CSRF token from cookies.
 *
 * Django stores the CSRF token in a cookie that needs to be included
 * in POST, PUT, DELETE, and PATCH requests for security.
 *
 * @param {string} name - Name of the cookie (usually 'csrftoken')
 * @returns {string|null} The CSRF token value or null if not found
 *
 * @example
 * const csrftoken = getCookie('csrftoken');
 * fetch(url, {
 *     method: 'POST',
 *     headers: {'X-CSRFToken': csrftoken}
 * });
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Get Django CSRF token.
 *
 * Convenience function that specifically retrieves the Django CSRF token.
 *
 * @returns {string|null} The CSRF token or null if not found
 *
 * @example
 * const token = getCSRFToken();
 * headers['X-CSRFToken'] = token;
 */
function getCSRFToken() {
    return getCookie('csrftoken');
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCookie,
        getCSRFToken
    };
}
