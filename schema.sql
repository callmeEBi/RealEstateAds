-- This SQL schema corresponds to the SQLAlchemy models in models.py.

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at DATETIME NOT NULL,

    CONSTRAINT check_user_role
        CHECK (role IN ('user', 'admin'))
);

CREATE INDEX ix_user_email
ON user (email);


CREATE TABLE listing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    location VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    area FLOAT,
    contact_phone VARCHAR(20),
    contact_social VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    user_id INTEGER NOT NULL,

    CONSTRAINT fk_listing_user
        FOREIGN KEY (user_id)
        REFERENCES user (id),

    CONSTRAINT check_price_non_negative
        CHECK (price >= 0),

    CONSTRAINT check_bedrooms_non_negative
        CHECK (bedrooms IS NULL OR bedrooms >= 0),

    CONSTRAINT check_bathrooms_non_negative
        CHECK (bathrooms IS NULL OR bathrooms >= 0),

    CONSTRAINT check_area_non_negative
        CHECK (area IS NULL OR area >= 0),

    CONSTRAINT check_listing_status
        CHECK (status IN ('pending', 'approved', 'rejected'))
);

CREATE INDEX ix_listing_price
ON listing (price);

CREATE INDEX ix_listing_location
ON listing (location);

CREATE INDEX ix_listing_property_type
ON listing (property_type);

CREATE INDEX ix_listing_status
ON listing (status);

CREATE INDEX ix_listing_created_at
ON listing (created_at);

CREATE INDEX ix_listing_user_id
ON listing (user_id);


CREATE TABLE image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(200) NOT NULL,
    listing_id INTEGER NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_image_listing
        FOREIGN KEY (listing_id)
        REFERENCES listing (id)
);

CREATE INDEX ix_image_listing_id
ON image (listing_id);
