// Global helper functions

/**
 * Wrapper for fetch with JSON and non-JSON error handling.
 * This prevents errors like:
 * Unexpected token '<', "<!doctype..." is not valid JSON
 */
async function apiFetch(url, options = {}) {
  const headers =
    options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json", ...(options.headers || {}) }
      : { ...(options.headers || {}) };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : { error: await response.text() };

  if (!response.ok) {
    throw new Error(data.error || data.message || "An error occurred");
  }

  return data;
}

/**
 * Simple HTML escaping helper.
 * Useful when inserting user data into template strings.
 */
function escapeHTML(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

/**
 * Compatibility helper.
 * Some of your pages call sanitizeHTML().
 * This version uses DOMPurify if available, otherwise falls back to escaping.
 */
function sanitizeHTML(value) {
  if (typeof DOMPurify !== "undefined") {
    return DOMPurify.sanitize(value);
  }

  return escapeHTML(value);
}

/**
 * Common mobile navigation toggle.
 */
function initNavToggle() {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");

  if (!toggle || !links) return;

  toggle.addEventListener("click", function (e) {
    e.stopPropagation();
    links.classList.toggle("open");
    toggle.classList.toggle("active");
  });

  document.addEventListener("click", function (e) {
    if (!links.contains(e.target) && !toggle.contains(e.target)) {
      links.classList.remove("open");
      toggle.classList.remove("active");
    }
  });
}

document.addEventListener("DOMContentLoaded", initNavToggle);
