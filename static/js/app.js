// Global helper functions

/**
 * Wrapper for fetch with JSON error handling.
 * If the response is not ok, throws an error with the server message.
 */
async function apiFetch(url, options = {}) {
    const headers = options.body && !(options.body instanceof FormData)
        ? { 'Content-Type': 'application/json', ...options.headers }
        : { ...options.headers };

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || data.message || 'An error occurred');
    }
    return data;
}
