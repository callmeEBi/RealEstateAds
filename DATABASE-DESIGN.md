# Database Design - Real Estate Listing Platform

## 1. Database Overview

This project uses a relational database to store users, property listings, and listing images.

The database is implemented using:

- SQLite for development
- SQLAlchemy ORM in Flask
- Python model classes in `models.py`

Although the tables are written as Python classes, SQLAlchemy converts these classes into actual database tables.

The database has three main tables:

1. `user`
2. `listing`
3. `image`

---

## 2. Main Entities

### User

The `user` table stores information about registered users.

A user can be:

- a normal user
- an admin

Admins can approve or reject property listings.

Important fields:

- `id`
- `name`
- `email`
- `password_hash`
- `phone`
- `role`
- `created_at`

---

### Listing

The `listing` table stores real-estate advertisements.

Each listing belongs to one user.

Important fields:

- `id`
- `title`
- `description`
- `price`
- `location`
- `property_type`
- `bedrooms`
- `bathrooms`
- `area`
- `status`
- `user_id`

The `status` field supports the admin review process.

Valid listing statuses are:

- `pending`
- `approved`
- `rejected`

---

### Image

The `image` table stores uploaded image filenames.

The actual image files are stored in the `uploads` folder. The database only stores the filename.

This is better than storing large image files directly inside the database.

Important fields:

- `id`
- `filename`
- `listing_id`
- `order`
- `created_at`

---

## 3. Entity Relationship Diagram

```text
+-------------------+
|       user        |
+-------------------+
| PK id             |
| name              |
| email UNIQUE      |
| password_hash     |
| phone             |
| role              |
| created_at        |
+-------------------+
          |
          | 1
          |
          | creates
          |
          | many
+-------------------+
|      listing      |
+-------------------+
| PK id             |
| title             |
| description       |
| price             |
| location          |
| property_type     |
| bedrooms          |
| bathrooms         |
| area              |
| contact_phone     |
| contact_social    |
| status            |
| created_at        |
| updated_at        |
| FK user_id        |
+-------------------+
          |
          | 1
          |
          | has
          |
          | many
+-------------------+
|       image       |
+-------------------+
| PK id             |
| filename          |
| FK listing_id     |
| order             |
| created_at        |
+-------------------+
```
