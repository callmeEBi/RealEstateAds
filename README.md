# RealEstateAds

RealEstateAds is a Flask-based real estate listing web application. Users can register, log in, create property listings with images, browse approved listings, and contact sellers. Admin users can review, approve, or reject submitted listings.

---

## Features

- User registration and login
- Create, edit, and delete personal listings
- Upload multiple images per listing
- Browse approved listings
- Search by location, price range, and property type
- View listing details and seller contact information
- Admin approval system for new listings
- Responsive HTML/CSS/JavaScript frontend

---

## Tech Stack

- **Backend:** Flask, SQLAlchemy, SQLite
- **Authentication:** Flask-Login
- **Frontend:** HTML, CSS, JavaScript
- **File Uploads:** Local `uploads/` folder

---

## Project Structure

```text
RealEstateAds/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   └── auth.js
│   ├── admin.html
│   ├── create_listing.html
│   ├── dashboard.html
│   ├── edit_listing.html
│   ├── index.html
│   ├── listing_detail.html
│   ├── login.html
│   └── register.html
├── app.py
├── config.py
├── models.py
├── README.md
└── requirements.txt
```
````

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

The database and upload folders are created automatically on first run.

---

## Default Admin

A default admin account is created automatically if no admin exists.

```text
Email: admin@example.com
Password: admin123
```

Admin panel:

```text
http://localhost:5000/admin
```

---

## Main Routes

| Route           | Description                  |
| --------------- | ---------------------------- |
| `/`             | Home page and listing search |
| `/login`        | Login page                   |
| `/register`     | Register page                |
| `/dashboard`    | User listings dashboard      |
| `/create`       | Create listing page          |
| `/edit/<id>`    | Edit listing page            |
| `/listing/<id>` | Listing detail page          |
| `/admin`        | Admin approval panel         |

---

## API Endpoints

| Method   | Endpoint                           | Description                 |
| -------- | ---------------------------------- | --------------------------- |
| `POST`   | `/api/register`                    | Register user               |
| `POST`   | `/api/login`                       | Login user                  |
| `POST`   | `/api/logout`                      | Logout user                 |
| `GET`    | `/api/user`                        | Get current user            |
| `GET`    | `/api/listings`                    | Get approved listings       |
| `POST`   | `/api/listings`                    | Create listing              |
| `GET`    | `/api/listings/<id>`               | Get listing details         |
| `PUT`    | `/api/listings/<id>`               | Update listing              |
| `DELETE` | `/api/listings/<id>`               | Delete listing              |
| `GET`    | `/api/my-listings`                 | Get current user's listings |
| `GET`    | `/api/admin/listings`              | Get pending listings        |
| `POST`   | `/api/admin/listings/<id>/approve` | Approve listing             |
| `POST`   | `/api/admin/listings/<id>/reject`  | Reject listing              |

---

## Listing Approval Flow

1. User creates a listing.
2. Listing status is set to `pending`.
3. Admin reviews the listing.
4. Admin approves or rejects it.
5. Approved listings appear on the home page.

---

## Dependencies

```text
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.2
Flask-WTF==1.1.1
python-dotenv==1.0.0
Werkzeug==2.3.7
```

---

## Notes

- Uploaded images are stored in `uploads/`.
- SQLite database is created automatically.
- This project is intended for educational/class project use.

