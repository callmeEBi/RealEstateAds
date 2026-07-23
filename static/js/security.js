


async function fetchCsrfToken() {
    try {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        if (data.csrf_token) {
            
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


const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    
    if (url.startsWith('/api/') && !url.includes('/api/csrf-token')) {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            options.headers = options.headers || {};
            options.headers['X-CSRF-Token'] = meta.content;
        }
    }
    return originalFetch.call(this, url, options);
};



function sanitizeHTML(dirty) {
    if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(dirty);
    }
    
    const div = document.createElement('div');
    div.textContent = dirty;
    return div.innerHTML;
}


function setSafeText(element, text) {
    if (element) {
        element.textContent = text;
    }
}


function setSafeHTML(element, html) {
    if (element) {
        element.innerHTML = sanitizeHTML(html);
    }
}


document.addEventListener('DOMContentLoaded', fetchCsrfToken);

