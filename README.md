# Real‑Estate Listing Platform

A full‑stack web application where sellers can list properties with photos, and buyers can browse, search, and contact sellers. Admin users review and approve all listings before they go live.

## Features
- User registration and login (session‑based, Flask‑Login)
- Create, edit, and delete your own property listings
- Upload multiple images per listing
- Search and filter listings by location, price range, and property type
- Contact seller via phone or social media (displayed on detail page)
- Admin panel to approve or reject pending listings
- Responsive, pure HTML/CSS/JS frontend

## Tech Stack
- **Backend**: Flask (Python), SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: Flask‑Login with hashed passwords
- **File Upload**: Flask, stored in `uploads/` folder

## Project Structure
```

project/
├── app.py                 # Main Flask application
├── models.py              # Database models (User, Listing, Image)
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── uploads/               # Uploaded images (created at runtime)
├── static/                # All frontend assets
│   ├── index.html         # Homepage – browse listings
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html     # Seller’s listing management
│   ├── create_listing.html
│   ├── edit_listing.html
│   ├── admin.html         # Admin panel
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js         # Common helpers (fetch, UI)
│       ├── auth.js        # Login/register logic
│       └── api.js         # API calls
└── instance/              # SQLite database file (created at runtime)

```

## Setup & Run

1. **Clone or download** this project into a folder.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

```
pip install -r requirements.txt
```
4. **Create a `.env` file** from the example:

```
cp .env.example .env
```

(Optionally change the `SECRET_KEY` to a random string.)
5. **Initialize the database** (first run only):

```
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

Or simply run the app – it will create the database file if missing.
6. **Run the application**:

```
python app.py
```

The server will start at `http://localhost:5000`.
7. **Create an admin user** (optional – you can promote a user via the shell):

```
flask shell
>>> from models import User, db
>>> user = User.query.filter_by(email='admin@example.com').first()
>>> user.role = 'admin'
>>> db.session.commit()
>>> exit()
```
8. Open your browser and go to `http://localhost:5000`.

## API Endpoints (for reference)

- `POST /api/register` – Register a new user
- `POST /api/login` – Log in
- `POST /api/logout` – Log out
- `GET /api/listings` – Get all approved listings (with search/filter)
- `POST /api/listings` – Create a new listing (auth required)
- `GET /api/listings/<id>` – Get a single listing
- `PUT /api/listings/<id>` – Update a listing (owner only)
- `DELETE /api/listings/<id>` – Delete a listing (owner or admin)
- `GET /api/my-listings` – Get listings of the current user
- `GET /api/admin/listings` – Get all pending listings (admin only)
- `POST /api/admin/listings/<id>/approve` – Approve a listing
- `POST /api/admin/listings/<id>/reject` – Reject a listing
- `GET /api/user` – Get current user info

## Deployment Notes

- For production, change `SECRET_KEY` to a strong random string.
- Use a proper database (PostgreSQL) by updating `DATABASE_URL` in `.env`.
- Serve static files via a web server (Nginx) or use `Whitenoise` for better performance.

## License

MIT (or as required by your institution)

