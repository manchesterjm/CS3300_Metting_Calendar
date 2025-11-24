/**
 * Password Generator Utility
 *
 * Provides client-side password generation functionality using the Django backend API.
 * Generates secure random passwords and populates password fields.
 *
 * @module password_generator
 * @requires csrf_utils
 */

/**
 * Generate a secure random password using the server API.
 *
 * Calls the Django backend to generate a secure random password
 * and populates the password fields in the form.
 *
 * @async
 * @param {HTMLButtonElement} btn - The button that was clicked (for UI feedback)
 * @param {string} apiUrl - The URL to the password generation API endpoint
 * @param {string} password1Id - ID of the first password field (default: 'id_password1')
 * @param {string} password2Id - ID of the second password field (default: 'id_password2')
 * @returns {Promise<void>}
 *
 * @example
 * <button onclick="generatePassword(this, '/api/generate-password/')">Generate</button>
 */
async function generatePassword(btn, apiUrl, password1Id = 'id_password1', password2Id = 'id_password2') {
    try {
        // Get CSRF token (requires csrf_utils.js to be loaded first)
        const csrftoken = getCookie('csrftoken');

        // Disable button and show loading state
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Generating...';

        // Call API to generate password
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.password) {
            // Populate password fields
            const password1 = document.getElementById(password1Id);
            const password2 = document.getElementById(password2Id);

            if (password1) password1.value = data.password;
            if (password2) password2.value = data.password;

            // Visual feedback
            btn.textContent = '✓ Generated!';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            }, 2000);
        } else {
            throw new Error('No password in response');
        }
    } catch (error) {
        console.error('Password generation failed:', error);

        // Show error to user
        btn.textContent = '✗ Error';
        btn.style.backgroundColor = '#e74c3c';

        setTimeout(() => {
            btn.textContent = 'Generate Password';
            btn.style.backgroundColor = '';
            btn.disabled = false;
        }, 3000);

        alert('Failed to generate password. Please try again or enter manually.');
    }
}

/**
 * Generate and copy password to clipboard.
 *
 * Generates a password and also copies it to the clipboard for easy pasting.
 *
 * @async
 * @param {HTMLButtonElement} btn - The button that was clicked
 * @param {string} apiUrl - The URL to the password generation API endpoint
 * @returns {Promise<void>}
 */
async function generateAndCopyPassword(btn, apiUrl) {
    await generatePassword(btn, apiUrl);

    // Get the generated password and copy to clipboard
    const password1 = document.getElementById('id_password1');
    if (password1 && password1.value) {
        try {
            await navigator.clipboard.writeText(password1.value);
            console.log('Password copied to clipboard');
        } catch (err) {
            console.error('Failed to copy password:', err);
        }
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generatePassword,
        generateAndCopyPassword
    };
}
