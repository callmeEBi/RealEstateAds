# RealEstateAds

![Python](https://img.shields.io/badge/python-3.x-blue) ![Flask](https://img.shields.io/badge/flask-2.3-black) ![SQLite](https://img.shields.io/badge/sqlite-dev-lightgrey)

A Flask-based real estate listing platform. Users register, post listings
with photos, browse approved listings, and contact sellers directly; admins
review each submission and approve or reject it before it goes live.

## Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Default Admin Account](#default-admin-account)
- [Routes](#routes)
- [API Endpoints](#api-endpoints)
- [How Approval Works](#how-approval-works)
- [Documentation](#documentation)
- [Dependencies](#dependencies)
- [Notes](#notes)

## Features

- User registration and login
- Create, edit, and delete personal listings
- Upload multiple images per listing
- Browse approved listings
- Search by location, price range, and property type
- View listing details and seller contact information
- Admin approval system for new listings
- Responsive HTML/CSS/JavaScript frontend

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, SQLite
- **Authentication:** Flask-Login (session-based)
- **Frontend:** HTML, CSS, vanilla JavaScript
- **File uploads:** local `uploads/` folder, filenames randomized on save

## Project Structure

```text
RealEstateAds/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   ├── auth.js
│   │   └── security.js
│   ├── admin.html
│   ├── create_listing.html
│   ├── dashboard.html
│   ├── edit_listing.html
│   ├── index.html
│   ├── listing_detail.html
│   ├── login.html
│   └── register.html
├── images/
│   └── main_logo.jpg
├── app.py
├── config.py
├── models.py
├── schema.sql              # raw SQL version of the schema in models.py
├── requirements.txt
├── README.md
└── DATABASE-DESIGN.md
```

## Getting Started

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```text
SECRET_KEY=your-random-secret-key-here
```

Generate one quickly with:

```bash
python -c "import os; print(os.urandom(24).hex())"
```

If you skip this, the app generates a temporary key for the session — fine
for a quick test, but your login sessions won't survive a restart.

### 4. Run the app

```bash
python app.py
```

Open **http://localhost:5000** — the database and `uploads/` folder are
created automatically on first run.

## Default Admin Account

No admin account exists by default. Create one from the command line once
the app has run at least once (so the database exists):

```bash
flask create-admin admin@example.com yourpassword --name "Admin"
```

Running this again with an email that's already registered promotes that
user to admin — their existing password is left untouched.

Admin panel: **http://localhost:5000/admin**

## Routes

| Route | Description |
|---|---|
| `/` | Home page and listing search |
| `/login` | Login page |
| `/register` | Register page |
| `/dashboard` | User's listings dashboard |
| `/create` | Create listing page |
| `/edit/<id>` | Edit listing page |
| `/listing/<id>` | Listing detail page |
| `/admin` | Admin approval panel |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register user |
| `POST` | `/api/login` | Login user |
| `POST` | `/api/logout` | Logout user |
| `GET` | `/api/user` | Get current user |
| `GET` | `/api/listings` | Get approved listings |
| `POST` | `/api/listings` | Create listing |
| `GET` | `/api/listings/<id>` | Get listing details |
| `PUT` | `/api/listings/<id>` | Update listing |
| `DELETE` | `/api/listings/<id>` | Delete listing |
| `GET` | `/api/my-listings` | Get current user's listings |
| `GET` | `/api/admin/listings` | Get pending listings |
| `POST` | `/api/admin/listings/<id>/approve` | Approve listing |
| `POST` | `/api/admin/listings/<id>/reject` | Reject listing |

Full detail, including auth requirements per endpoint, is in
[DOCUMENTATION.md](./DOCUMENTATION.md#6-api-documentation).

## How Approval Works

1. User creates (or edits) a listing.
2. Listing status is set to `pending`.
3. Admin reviews it.
4. Admin approves or rejects it.
5. Approved listings appear on the home page.

Full step-by-step walkthrough (request → validation → DB → response) is in
[DOCUMENTATION.md](./DOCUMENTATION.md#43-sequence-diagram--create-listing).

## Documentation

This README covers running the app. For the full project write-up:

- **Official DOCUMENTATION** — requirements analysis, UML
  diagrams (use case, class, sequence), architecture, full API reference,
  and verified test results
- **[DATABASE-DESIGN.md](./DATABASE-DESIGN.md)** — entity breakdown and ER
  diagram
- **[schema.sql](./schema.sql)** — raw SQL schema, if you want to set up
  the database without going through SQLAlchemy

## Dependencies

Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, python-dotenv, Werkzeug.
Exact pinned versions: see [requirements.txt](./requirements.txt).

## Notes

- Uploaded images are stored in `uploads/`; the SQLite database is created
  automatically.
- Local file storage works for development but won't survive most free
  hosting platforms as-is — see `DOCUMENTATION.md` for the deployment plan.
- This project is intended for educational/class project use.
