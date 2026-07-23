# Security & Pagination Updates

This ZIP contains the modified files described in the review.

## Key Changes

1. **XSS Protection**: All pages now include DOMPurify and use `sanitizeHTML()` before inserting user‑supplied data into the DOM.

2. **CSRF Protection**:
   - Flask‑WTF's `CsrfProtect` is enabled.
   - A new endpoint `/api/csrf-token` provides a token.
   - The `security.js` script automatically adds the token to all `fetch` requests to `/api/*` (except the token endpoint).

3. **Strong Secret Key**:
   - `config.py` now raises an error if `SECRET_KEY` is missing in production.
   - A random key is generated for development (but you should still set it in `.env`).

4. **Numeric Field Validation**:
   - `safe_float()` and `safe_int()` helpers handle conversion errors.
   - All endpoints using numeric fields now validate and return meaningful errors.

5. **Pagination**:
   - `/api/listings` accepts `page` and `per_page` parameters.
   - Response includes `meta` with total count, page, etc.
   - The frontend `loadListings` function now handles pagination and displays prev/next buttons.

## Next Steps

1. Install the updated dependencies:

```

pip install -r requirements.txt

```

(Flask-WTF is already present; you may also need `email-validator` if you add email validation.)

2. Set a strong `SECRET_KEY` in your `.env` file.

3. If you have existing data, run migrations (if using Alembic) – but this is a SQLite file, you can just drop and recreate.

4. Test thoroughly.

For a complete deployment, also consider:

- Using PostgreSQL in production.
- Enabling HTTPS.
- Adding logging and monitoring.
