# User Impersonation System for Administrators
# Simple Flask app for learning authentication and admin features
# This is my first attempt at building user impersonation logic

from flask import Flask, jsonify, request, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import hashlib

# Create Flask app
app = Flask(__name__)

# Simple configuration - keeping it basic for learning
app.config['SECRET_KEY'] = 'my-secret-key-for-sessions'  # TODO: change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Simple User model - keeping it basic for learning
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # This determines if user can impersonate others
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

# Simple Activity Log model - to track impersonation activities
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    impersonated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'start_impersonation', 'end_impersonation'
    timestamp = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(50))

# Helper functions - keeping them simple for learning
def hash_password(password):
    """Simple password hashing - using basic method for learning"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed):
    """Check if password matches hash"""
    return hash_password(password) == hashed

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def is_admin():
    """Check if current user is admin"""
    if not is_logged_in():
        return False
    user = User.query.get(session['user_id'])
    return user and user.is_admin

def get_current_user():
    """Get current user object"""
    if not is_logged_in():
        return None
    return User.query.get(session['user_id'])

def get_effective_user():
    """Get the user we're currently acting as (could be impersonated user)"""
    if 'impersonated_user_id' in session:
        return User.query.get(session['impersonated_user_id'])
    return get_current_user()

# Routes - keeping them simple and easy to understand
@app.route('/')
def home():
    """Home page - shows login status and available actions"""
    current_user = get_current_user()
    effective_user = get_effective_user()

    if not current_user:
        return jsonify({
            'message': 'User Impersonation System',
            'status': 'Not logged in',
            'actions': ['POST /login', 'POST /register']
        })

    response_data = {
        'message': 'User Impersonation System',
        'status': 'Logged in',
        'current_user': {
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        },
        'actions': ['GET /dashboard', 'POST /logout']
    }

    # If we're impersonating someone
    if effective_user.id != current_user.id:
        response_data['impersonation'] = {
            'acting_as': {
                'id': effective_user.id,
                'username': effective_user.username
            },
            'actions': ['POST /stop-impersonation']
        }

    # If user is admin, show impersonation options
    if current_user.is_admin:
        response_data['admin_actions'] = ['GET /users', 'POST /impersonate']

    return jsonify(response_data)

@app.route('/register', methods=['GET'])
def register_form():
    """Show registration form using template"""
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form using template"""
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    """Register a new user - handles both JSON and form data"""
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'is_admin': request.form.get('is_admin') == 'on'
        }

    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        if request.is_json:
            return jsonify({'error': 'Username, email, and password required'}), 400
        else:
            return render_template('error.html',
                                 error_message='Username, email, and password required',
                                 back_url='/register',
                                 back_text='Try again')

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        error_msg = 'Username already exists'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        else:
            return render_template('error.html',
                                 error_message=error_msg,
                                 back_url='/register',
                                 back_text='Try again')

    if User.query.filter_by(email=data['email']).first():
        error_msg = 'Email already exists'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        else:
            return render_template('error.html',
                                 error_message=error_msg,
                                 back_url='/register',
                                 back_text='Try again')

    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        is_admin=data.get('is_admin', False)  # Only for demo - normally this would be restricted
    )

    db.session.add(new_user)
    db.session.commit()

    if request.is_json:
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'is_admin': new_user.is_admin
            }
        })
    else:
        return render_template('success.html',
                             success_message=f'User {new_user.username} registered successfully!',
                             details={
                                 'Username': new_user.username,
                                 'Email': new_user.email,
                                 'Admin': 'Yes' if new_user.is_admin else 'No'
                             },
                             next_url='/login',
                             next_text='Login now')

@app.route('/login', methods=['POST'])
def login():
    """Login user - handles both JSON and form data"""
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }

    if not data or not data.get('username') or not data.get('password'):
        if request.is_json:
            return jsonify({'error': 'Username and password required'}), 400
        else:
            return render_template('error.html',
                                 error_message='Username and password required',
                                 back_url='/login',
                                 back_text='Try again')

    # Find user
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password(data['password'], user.password_hash):
        error_msg = 'Invalid username or password'
        if request.is_json:
            return jsonify({'error': error_msg}), 401
        else:
            return render_template('error.html',
                                 error_message=error_msg,
                                 back_url='/login',
                                 back_text='Try again')

    # Set session
    session['user_id'] = user.id
    user.last_login = datetime.now()
    db.session.commit()

    if request.is_json:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    else:
        return redirect('/dashboard')

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user and end any impersonation"""
    if not is_logged_in():
        return jsonify({'error': 'Not logged in'}), 401

    # End impersonation if active
    if 'impersonated_user_id' in session:
        session.pop('impersonated_user_id')

    session.pop('user_id')

    return jsonify({'message': 'Logged out successfully'})

@app.route('/users')
def get_users():
    """Get all users - only for admins"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    users = User.query.all()
    user_list = []

    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
        })

    return jsonify({
        'users': user_list,
        'total': len(user_list)
    })

@app.route('/impersonate', methods=['POST'])
def start_impersonation():
    """Start impersonating another user - CORE FEATURE"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    target_user_id = data.get('user_id')

    if not target_user_id:
        return jsonify({'error': 'user_id required'}), 400

    # Find target user
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # Don't allow impersonating other admins (security check)
    if target_user.is_admin:
        return jsonify({'error': 'Cannot impersonate other administrators'}), 403

    # Don't allow impersonating yourself
    current_user = get_current_user()
    if target_user.id == current_user.id:
        return jsonify({'error': 'Cannot impersonate yourself'}), 400

    # Start impersonation
    session['impersonated_user_id'] = target_user.id

    # Log the impersonation activity
    activity = ActivityLog(
        admin_user_id=current_user.id,
        impersonated_user_id=target_user.id,
        action='start_impersonation',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({
        'message': f'Now impersonating {target_user.username}',
        'admin_user': {
            'id': current_user.id,
            'username': current_user.username
        },
        'impersonated_user': {
            'id': target_user.id,
            'username': target_user.username,
            'email': target_user.email
        },
        'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/stop-impersonation', methods=['POST'])
def stop_impersonation():
    """Stop impersonating and return to admin user"""
    if not is_logged_in():
        return jsonify({'error': 'Not logged in'}), 401

    if 'impersonated_user_id' not in session:
        return jsonify({'error': 'Not currently impersonating anyone'}), 400

    # Get users for logging
    current_user = get_current_user()
    impersonated_user = User.query.get(session['impersonated_user_id'])

    # End impersonation
    session.pop('impersonated_user_id')

    # Log the end of impersonation
    activity = ActivityLog(
        admin_user_id=current_user.id,
        impersonated_user_id=impersonated_user.id,
        action='end_impersonation',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({
        'message': f'Stopped impersonating {impersonated_user.username}',
        'admin_user': {
            'id': current_user.id,
            'username': current_user.username
        },
        'ended_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/dashboard')
def dashboard():
    """User dashboard - shows different content based on effective user"""
    if not is_logged_in():
        return jsonify({'error': 'Login required'}), 401

    current_user = get_current_user()
    effective_user = get_effective_user()

    dashboard_data = {
        'message': f'Welcome to {effective_user.username}\'s dashboard',
        'user_info': {
            'id': effective_user.id,
            'username': effective_user.username,
            'email': effective_user.email,
            'is_admin': effective_user.is_admin,
            'last_login': effective_user.last_login.strftime('%Y-%m-%d %H:%M:%S') if effective_user.last_login else 'Never'
        }
    }

    # If we're impersonating, show that info
    if effective_user.id != current_user.id:
        dashboard_data['impersonation_info'] = {
            'message': f'You are viewing {effective_user.username}\'s dashboard',
            'admin_user': current_user.username,
            'impersonated_user': effective_user.username
        }

    return jsonify(dashboard_data)

@app.route('/activity-log')
def get_activity_log():
    """Get impersonation activity log - only for admins"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    activity_list = []

    for activity in activities:
        admin_user = User.query.get(activity.admin_user_id)
        impersonated_user = User.query.get(activity.impersonated_user_id)

        activity_list.append({
            'id': activity.id,
            'admin_user': admin_user.username if admin_user else 'Unknown',
            'impersonated_user': impersonated_user.username if impersonated_user else 'Unknown',
            'action': activity.action,
            'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': activity.ip_address
        })

    return jsonify({
        'activities': activity_list,
        'total': len(activity_list)
    })

def create_sample_users():
    """Create sample users for testing - keeping it simple for learning"""
    sample_users = [
        {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123', 'is_admin': True},
        {'username': 'pratiksha', 'email': 'pratiksha@example.com', 'password': 'pratiksha123', 'is_admin': False},
        {'username': 'anand', 'email': 'anand@example.com', 'password': 'anand123', 'is_admin': False},
        {'username': 'pallavi', 'email': 'pallavi@example.com', 'password': 'pallavi123', 'is_admin': False},
    ]

    for user_data in sample_users:
        # Check if user already exists
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=hash_password(user_data['password']),
                is_admin=user_data['is_admin']
            )
            db.session.add(user)

    db.session.commit()
    print("Sample users created:")
    print("- admin/admin123 (Administrator)")
    print("- pratiksha/pratiksha123 (Regular user)")
    print("- anand/anand123 (Regular user)")
    print("- pallavi/pallavi123 (Regular user)")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")

        # Always recreate sample users for demo purposes
        print("Clearing existing users and adding fresh sample users...")
        User.query.delete()
        ActivityLog.query.delete()
        db.session.commit()
        create_sample_users()
        print("Sample users added!")

    print("Starting User Impersonation System...")
    print("Available endpoints:")
    print("- GET / - Home page (shows login status)")
    print("- POST /register - Register new user")
    print("- POST /login - Login user")
    print("- POST /logout - Logout user")
    print("- GET /users - List all users (admin only)")
    print("- POST /impersonate - Start impersonating user (admin only)")
    print("- POST /stop-impersonation - Stop impersonating")
    print("- GET /dashboard - User dashboard")
    print("- GET /activity-log - View impersonation log (admin only)")
    print()
    print("Test with these sample users:")
    print("- admin/admin123 (Administrator - can impersonate others)")
    print("- pratiksha/pratiksha123 (Regular user)")
    print("- anand/anand123 (Regular user)")
    print("- pallavi/pallavi123 (Regular user)")

    app.run(debug=True, port=5002)
