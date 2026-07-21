import os
import uuid
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Listing, Image
import click

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails'), exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_files(files, listing_id):
    """Save multiple files and create Image records."""
    uploaded = []
    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(filepath)
            # Create Image record
            img = Image(filename=new_filename, listing_id=listing_id, order=i)
            db.session.add(img)
            uploaded.append(new_filename)
    return uploaded

# --- Routes for serving HTML pages ---
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('static', 'register.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    return send_from_directory('static', 'dashboard.html')

@app.route('/create')
@login_required
def create_page():
    return send_from_directory('static', 'create_listing.html')

@app.route('/edit/<int:listing_id>')
@login_required
def edit_page(listing_id):
    return send_from_directory('static', 'edit_listing.html')

@app.route('/admin')
@login_required
def admin_page():
    # Check admin role
    if current_user.role != 'admin':
        return "Unauthorized", 403
    return send_from_directory('static', 'admin.html')

# NEW: listing detail page
@app.route('/listing/<int:listing_id>')
def listing_detail_page(listing_id):
    return send_from_directory('static', 'listing_detail.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- API Routes ---

# Authentication
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(name=name, email=email, phone=phone, role='user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    login_user(user)
    return jsonify({
        'message': 'Logged in',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role
    })

# Listings (public)
@app.route('/api/listings', methods=['GET'])
def get_listings():
    # Query parameters for filtering
    location = request.args.get('location', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    property_type = request.args.get('property_type', '')

    query = Listing.query.filter_by(status='approved')

    if location:
        query = query.filter(Listing.location.ilike(f'%{location}%'))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if property_type:
        query = query.filter_by(property_type=property_type)

    listings = query.order_by(Listing.created_at.desc()).all()
    result = []
    for listing in listings:
        result.append({
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'price': listing.price,
            'location': listing.location,
            'property_type': listing.property_type,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
            'area': listing.area,
            'contact_phone': listing.contact_phone,
            'contact_social': listing.contact_social,
            'created_at': listing.created_at.isoformat(),
            'images': [{'filename': img.filename} for img in listing.images]
        })
    return jsonify(result)

@app.route('/api/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.status != 'approved' and (not current_user.is_authenticated or current_user.id != listing.user_id):
        return jsonify({'error': 'Listing not available'}), 403

    return jsonify({
        'id': listing.id,
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'location': listing.location,
        'property_type': listing.property_type,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'area': listing.area,
        'contact_phone': listing.contact_phone,
        'contact_social': listing.contact_social,
        'status': listing.status,
        'created_at': listing.created_at.isoformat(),
        'seller': {
            'id': listing.seller.id,
            'name': listing.seller.name,
            'phone': listing.seller.phone,
            'email': listing.seller.email
        },
        'images': [{'filename': img.filename} for img in listing.images]
    })

# Create listing (authenticated)
@app.route('/api/listings', methods=['POST'])
@login_required
def create_listing():
    # Handle form data with files
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    location = request.form.get('location')
    property_type = request.form.get('property_type')
    bedrooms = request.form.get('bedrooms', type=int)
    bathrooms = request.form.get('bathrooms', type=int)
    area = request.form.get('area', type=float)
    contact_phone = request.form.get('contact_phone')
    contact_social = request.form.get('contact_social', '')

    if not all([title, description, price, location, property_type]):
        return jsonify({'error': 'Missing required fields'}), 400

    listing = Listing(
        title=title,
        description=description,
        price=float(price),
        location=location,
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area=area,
        contact_phone=contact_phone,
        contact_social=contact_social,
        user_id=current_user.id
    )
    db.session.add(listing)
    db.session.commit()

    # Handle image uploads
    files = request.files.getlist('images')
    if files:
        save_uploaded_files(files, listing.id)

    db.session.commit()
    return jsonify({'message': 'Listing created', 'id': listing.id}), 201

# Update listing (owner only)
@app.route('/api/listings/<int:listing_id>', methods=['PUT'])
@login_required
def update_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user_id != current_user.id:
        return jsonify({'error': 'You can only edit your own listings'}), 403

    # Parse form data
    listing.title = request.form.get('title', listing.title)
    listing.description = request.form.get('description', listing.description)
    listing.price = float(request.form.get('price', listing.price))
    listing.location = request.form.get('location', listing.location)
    listing.property_type = request.form.get('property_type', listing.property_type)
    listing.bedrooms = request.form.get('bedrooms', type=int) or listing.bedrooms
    listing.bathrooms = request.form.get('bathrooms', type=int) or listing.bathrooms
    listing.area = request.form.get('area', type=float) or listing.area
    listing.contact_phone = request.form.get('contact_phone', listing.contact_phone)
    listing.contact_social = request.form.get('contact_social', listing.contact_social)

    # Handle new image uploads (append)
    files = request.files.getlist('images')
    if files:
        save_uploaded_files(files, listing.id)

    db.session.commit()
    return jsonify({'message': 'Listing updated'})

# Delete listing (owner or admin)
@app.route('/api/listings/<int:listing_id>', methods=['DELETE'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403

    # Delete associated images from filesystem
    for img in listing.images:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(listing)
    db.session.commit()
    return jsonify({'message': 'Listing deleted'})

# My listings (for seller dashboard)
@app.route('/api/my-listings', methods=['GET'])
@login_required
def my_listings():
    listings = Listing.query.filter_by(user_id=current_user.id).order_by(Listing.created_at.desc()).all()
    result = []
    for listing in listings:
        result.append({
            'id': listing.id,
            'title': listing.title,
            'price': listing.price,
            'location': listing.location,
            'status': listing.status,
            'created_at': listing.created_at.isoformat(),
            'image_count': len(listing.images)
        })
    return jsonify(result)

# Admin endpoints
@app.route('/api/admin/listings', methods=['GET'])
@login_required
def admin_listings():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    listings = Listing.query.filter_by(status='pending').order_by(Listing.created_at.desc()).all()
    result = []
    for listing in listings:
        result.append({
            'id': listing.id,
            'title': listing.title,
            'price': listing.price,
            'location': listing.location,
            'seller_name': listing.seller.name,
            'created_at': listing.created_at.isoformat(),
            'images': [{'filename': img.filename} for img in listing.images]
        })
    return jsonify(result)

@app.route('/api/admin/listings/<int:listing_id>/approve', methods=['POST'])
@login_required
def approve_listing(listing_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    listing = Listing.query.get_or_404(listing_id)
    listing.status = 'approved'
    db.session.commit()
    return jsonify({'message': 'Listing approved'})

@app.route('/api/admin/listings/<int:listing_id>/reject', methods=['POST'])
@login_required
def reject_listing(listing_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    listing = Listing.query.get_or_404(listing_id)
    listing.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Listing rejected'})

# ---------- Flask CLI command to create admin ----------
@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
@click.option("--name", default="Admin")
def create_admin_command(email, password, name):
    """Create an admin user with the given email and password."""
    user = User.query.filter_by(email=email).first()
    if user:
        click.echo(f"User {email} already exists. Updating role to admin.")
        user.role = 'admin'
    else:
        user = User(name=name, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo(f"Admin user {email} created/updated successfully.")

# ---------- Main entry point ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default admin if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(name='Default Admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@example.com / admin123")
    app.run(debug=True)
