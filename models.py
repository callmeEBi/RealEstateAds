from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __table_args__ = (
        db.CheckConstraint("role IN ('user', 'admin')", name="check_user_role"),
    )

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(200), nullable=False)

    phone = db.Column(db.String(20))

    role = db.Column(db.String(20), default="user", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    listings = db.relationship("Listing", backref="seller", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Listing(db.Model):
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="check_price_non_negative"),
        db.CheckConstraint(
            "bedrooms IS NULL OR bedrooms >= 0", name="check_bedrooms_non_negative"
        ),
        db.CheckConstraint(
            "bathrooms IS NULL OR bathrooms >= 0", name="check_bathrooms_non_negative"
        ),
        db.CheckConstraint("area IS NULL OR area >= 0", name="check_area_non_negative"),
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')", name="check_listing_status"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False, index=True)

    location = db.Column(db.String(100), nullable=False, index=True)

    property_type = db.Column(db.String(50), nullable=False, index=True)

    bedrooms = db.Column(db.Integer)

    bathrooms = db.Column(db.Integer)

    area = db.Column(db.Float)

    contact_phone = db.Column(db.String(20))

    contact_social = db.Column(db.String(100))

    status = db.Column(db.String(20), default="pending", nullable=False, index=True)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )

    images = db.relationship(
        "Image", backref="listing", lazy=True, cascade="all, delete-orphan"
    )


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(200), nullable=False)

    listing_id = db.Column(
        db.Integer, db.ForeignKey("listing.id"), nullable=False, index=True
    )

    order = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
