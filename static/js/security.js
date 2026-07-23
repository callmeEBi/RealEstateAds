// CSRF token management and XSS protection

// Fetch CSRF token from server and store in a meta tag or variable
async function fetchCsrfToken() {
    try {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        if (data.csrf_token) {
            // Store in a meta tag for easy access
            let meta = document.querySelector('meta[name="csrf-token"]');
            if (!meta) {
                meta = document.createElement('meta');
                meta.name = 'csrf-token';
                document.head.appendChild(meta);
            }
            meta.content = data.csrf_token;
        }
    } catch (e) {
        console.warn('Could not fetch CSRF token:', e);
    }
}

// Automatically add CSRF header to all fetch requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Only add for API calls (you can adjust the condition)
    if (url.startsWith('/api/') && !url.includes('/api/csrf-token')) {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            options.headers = options.headers || {};
            options.headers['X-CSRF-Token'] = meta.content;
        }
    }
    return originalFetch.call(this, url, options);
};

// DOMPurify integration – sanitize HTML before inserting
// Include DOMPurify from CDN (add to your HTML)
function sanitizeHTML(dirty) {
    if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(dirty);
    }
    // Fallback: escape basic HTML entities
    const div = document.createElement('div');
    div.textContent = dirty;
    return div.innerHTML;
}

// Helper: set text content safely (no HTML)
function setSafeText(element, text) {
    if (element) {
        element.textContent = text;
    }
}

// Helper: set HTML safely with sanitization
function setSafeHTML(element, html) {
    if (element) {
        element.innerHTML = sanitizeHTML(html);
    }
}

// Automatically fetch CSRF token on page load
document.addEventListener('DOMContentLoaded', fetchCsrfToken);

