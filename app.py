import os
import uuid
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    redirect,
    url_for,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from config import Config
from models import db, User, Listing, Image
import click

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config.from_object(Config)

# NOTE:
# CSRF protection has been removed for this class-project version.
# The frontend uses normal fetch() API requests, and CSRF was causing
# HTML error pages to be returned instead of JSON.

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "thumbnails"), exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    """
    Return JSON for API requests instead of redirecting to an HTML login page.
    This prevents frontend errors like:
    Unexpected token '<', "<!doctype..." is not valid JSON
    """
    if request.path.startswith("/api/"):
        return jsonify({"error": "Authentication required"}), 401
    return redirect(url_for("login_page"))


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_files(files, listing_id):
    """Save multiple files and create Image records."""
    uploaded = []

    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

            file.save(filepath)

            img = Image(filename=new_filename, listing_id=listing_id, order=i)
            db.session.add(img)
            uploaded.append(new_filename)

    return uploaded


def safe_float(value, default=None):
    """Convert to float, return default if conversion fails."""
    if value is None or value == "":
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=None):
    """Convert to int, return default if conversion fails."""
    if value is None or value == "":
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ---- Serve frontend pages ----

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/login")
def login_page():
    return send_from_directory("static", "login.html")


@app.route("/register")
def register_page():
    return send_from_directory("static", "register.html")


@app.route("/dashboard")
@login_required
def dashboard_page():
    return send_from_directory("static", "dashboard.html")


@app.route("/create")
@login_required
def create_page():
    return send_from_directory("static", "create_listing.html")


@app.route("/edit/<int:listing_id>")
@login_required
def edit_page(listing_id):
    return send_from_directory("static", "edit_listing.html")


@app.route("/admin")
@login_required
def admin_page():
    if current_user.role != "admin":
        return "Unauthorized", 403
    return send_from_directory("static", "admin.html")


@app.route("/listing/<int:listing_id>")
def listing_detail_page(listing_id):
    return send_from_directory("static", "listing_detail.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---- Auth endpoints ----

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(name=name, email=email, phone=phone, role="user")
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    return jsonify(
        {
            "message": "Logged in",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        }
    )


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@app.route("/api/user", methods=["GET"])
def get_user():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False}), 200

    return jsonify(
        {
            "authenticated": True,
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        }
    )


# ---- Listing endpoints ----

@app.route("/api/listings", methods=["GET"])
def get_listings():
    location = request.args.get("location", "")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    property_type = request.args.get("property_type", "")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)

    if page < 1:
        page = 1

    if per_page < 1 or per_page > 100:
        per_page = 12

    query = Listing.query.filter_by(status="approved")

    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))

    if min_price is not None:
        query = query.filter(Listing.price >= min_price)

    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    if property_type:
        query = query.filter_by(property_type=property_type)

    query = query.order_by(Listing.created_at.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    result = []

    for listing in paginated.items:
        images = sorted(listing.images, key=lambda img: img.order)

        result.append(
            {
                "id": listing.id,
                "title": listing.title,
                "description": listing.description,
                "price": listing.price,
                "location": listing.location,
                "property_type": listing.property_type,
                "bedrooms": listing.bedrooms,
                "bathrooms": listing.bathrooms,
                "area": listing.area,
                "contact_phone": listing.contact_phone,
                "contact_social": listing.contact_social,
                "created_at": listing.created_at.isoformat(),
                "images": [{"filename": img.filename} for img in images],
            }
        )

    return jsonify(
        {
            "data": result,
            "meta": {
                "total": paginated.total,
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total_pages": paginated.pages,
            },
        }
    )


@app.route("/api/listings/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    allowed = listing.status == "approved"

    if current_user.is_authenticated:
        allowed = (
            allowed
            or current_user.id == listing.user_id
            or current_user.role == "admin"
        )

    if not allowed:
        return jsonify({"error": "Listing not available"}), 403

    images = sorted(listing.images, key=lambda img: img.order)

    return jsonify(
        {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "location": listing.location,
            "property_type": listing.property_type,
            "bedrooms": listing.bedrooms,
            "bathrooms": listing.bathrooms,
            "area": listing.area,
            "contact_phone": listing.contact_phone,
            "contact_social": listing.contact_social,
            "status": listing.status,
            "created_at": listing.created_at.isoformat(),
            "seller": {
                "id": listing.seller.id,
                "name": listing.seller.name,
                "phone": listing.seller.phone,
                "email": listing.seller.email,
            },
            "images": [{"filename": img.filename} for img in images],
        }
    )


@app.route("/api/listings", methods=["POST"])
@login_required
def create_listing():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    price = safe_float(request.form.get("price"))
    location = request.form.get("location", "").strip()
    property_type = request.form.get("property_type", "").strip()

    bedrooms = safe_int(request.form.get("bedrooms"))
    bathrooms = safe_int(request.form.get("bathrooms"))
    area = safe_float(request.form.get("area"))

    contact_phone = request.form.get("contact_phone", "").strip()
    contact_social = request.form.get("contact_social", "").strip()

    if not title or not description or price is None or not location or not property_type:
        return jsonify({"error": "Missing required fields"}), 400

    if price < 0:
        return jsonify({"error": "Invalid price"}), 400

    if bedrooms is not None and bedrooms < 0:
        return jsonify({"error": "Invalid bedrooms"}), 400

    if bathrooms is not None and bathrooms < 0:
        return jsonify({"error": "Invalid bathrooms"}), 400

    if area is not None and area < 0:
        return jsonify({"error": "Invalid area"}), 400

    listing = Listing(
        title=title,
        description=description,
        price=price,
        location=location,
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area=area,
        contact_phone=contact_phone,
        contact_social=contact_social,
        user_id=current_user.id,
        status="pending",
    )

    db.session.add(listing)
    db.session.commit()

    files = request.files.getlist("images")

    if files:
        save_uploaded_files(files, listing.id)

    db.session.commit()

    return jsonify({"message": "Listing created", "id": listing.id}), 201


@app.route("/api/listings/<int:listing_id>", methods=["PUT"])
@login_required
def update_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.user_id != current_user.id:
        return jsonify({"error": "You can only edit your own listings"}), 403

    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    property_type = request.form.get("property_type")
    contact_phone = request.form.get("contact_phone")
    contact_social = request.form.get("contact_social")

    if title is not None:
        listing.title = title.strip()

    if description is not None:
        listing.description = description.strip()

    price_str = request.form.get("price")
    if price_str is not None:
        price = safe_float(price_str)

        if price is None or price < 0:
            return jsonify({"error": "Invalid price"}), 400

        listing.price = price

    if location is not None:
        listing.location = location.strip()

    if property_type is not None:
        listing.property_type = property_type.strip()

    bedrooms_str = request.form.get("bedrooms")
    if bedrooms_str is not None:
        bedrooms = safe_int(bedrooms_str)

        if bedrooms is not None and bedrooms < 0:
            return jsonify({"error": "Invalid bedrooms"}), 400

        listing.bedrooms = bedrooms

    bathrooms_str = request.form.get("bathrooms")
    if bathrooms_str is not None:
        bathrooms = safe_int(bathrooms_str)

        if bathrooms is not None and bathrooms < 0:
            return jsonify({"error": "Invalid bathrooms"}), 400

        listing.bathrooms = bathrooms

    area_str = request.form.get("area")
    if area_str is not None:
        area = safe_float(area_str)

        if area is not None and area < 0:
            return jsonify({"error": "Invalid area"}), 400

        listing.area = area

    if contact_phone is not None:
        listing.contact_phone = contact_phone.strip()

    if contact_social is not None:
        listing.contact_social = contact_social.strip()

    files = request.files.getlist("images")

    if files:
        save_uploaded_files(files, listing.id)

    # After editing, send listing back to admin review.
    listing.status = "pending"

    db.session.commit()

    return jsonify({"message": "Listing updated"})


@app.route("/api/listings/<int:listing_id>", methods=["DELETE"])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.user_id != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Permission denied"}), 403

    for img in listing.images:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], img.filename)

        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(listing)
    db.session.commit()

    return jsonify({"message": "Listing deleted"})


@app.route("/api/my-listings", methods=["GET"])
@login_required
def my_listings():
    listings = (
        Listing.query.filter_by(user_id=current_user.id)
        .order_by(Listing.created_at.desc())
        .all()
    )

    result = []

    for listing in listings:
        result.append(
            {
                "id": listing.id,
                "title": listing.title,
                "price": listing.price,
                "location": listing.location,
                "status": listing.status,
                "created_at": listing.created_at.isoformat(),
                "image_count": len(listing.images),
            }
        )

    return jsonify(result)


# ---- Admin endpoints ----

@app.route("/api/admin/listings", methods=["GET"])
@login_required
def admin_listings():
    if current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    listings = (
        Listing.query.filter_by(status="pending")
        .order_by(Listing.created_at.desc())
        .all()
    )

    result = []

    for listing in listings:
        images = sorted(listing.images, key=lambda img: img.order)

        result.append(
            {
                "id": listing.id,
                "title": listing.title,
                "price": listing.price,
                "location": listing.location,
                "seller_name": listing.seller.name,
                "created_at": listing.created_at.isoformat(),
                "images": [{"filename": img.filename} for img in images],
            }
        )

    return jsonify(result)


@app.route("/api/admin/listings/<int:listing_id>/approve", methods=["POST"])
@login_required
def approve_listing(listing_id):
    if current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    listing = Listing.query.get_or_404(listing_id)
    listing.status = "approved"

    db.session.commit()

    return jsonify({"message": "Listing approved"})


@app.route("/api/admin/listings/<int:listing_id>/reject", methods=["POST"])
@login_required
def reject_listing(listing_id):
    if current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    listing = Listing.query.get_or_404(listing_id)
    listing.status = "rejected"

    db.session.commit()

    return jsonify({"message": "Listing rejected"})


# ---- CLI command ----

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
@click.option("--name", default="Admin")
def create_admin_command(email, password, name):
    """Create an admin user with the given email and password."""
    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if user:
        click.echo(f"User {email} already exists. Updating role to admin.")
        user.role = "admin"
    else:
        user = User(name=name, email=email, role="admin")
        user.set_password(password)
        db.session.add(user)

    db.session.commit()

    click.echo(f"Admin user {email} created/updated successfully.")


# ---- Error handlers ----

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found"}), 404

    return send_from_directory("static", "index.html")


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
