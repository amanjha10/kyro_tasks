# 🎯 **PERFECT PROMPT FOR USER IMPERSONATION SYSTEM**

## **Task Description**
Create a Flask-based user impersonation system that allows authorized administrators to impersonate other users. The code should be written in a beginner-friendly style, as if someone learning Flask wrote it.

## **Detailed Requirements**

### **1. Core Functionality**
- **User Authentication**: Simple login/logout system with session management
- **Admin Impersonation**: Authorized admins can impersonate regular users
- **Session Management**: Proper handling of admin session + impersonated user session
- **Security Checks**: Prevent impersonating other admins, self-impersonation
- **Activity Logging**: Track all impersonation activities with timestamps

### **2. Database Models**
```python
# User model with admin flag
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

# Activity logging for impersonation
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    impersonated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))  # 'start_impersonation', 'end_impersonation'
    timestamp = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(50))
```

### **3. Key API Endpoints**
- `POST /login` - User login with username/password
- `GET /users` - List all users (admin only)
- `POST /impersonate` - Start impersonating user (admin only)
- `POST /stop-impersonation` - End impersonation
- `GET /dashboard` - Show current effective user
- `GET /activity-log` - View impersonation history (admin only)

### **4. Session Management Logic**
```python
# Session structure
session['user_id'] = admin_user.id              # The actual logged-in admin
session['impersonated_user_id'] = target_user.id # User being impersonated

# Helper functions
def get_current_user():
    """Get the actual logged-in admin"""
    return User.query.get(session['user_id'])

def get_effective_user():
    """Get the user we're currently acting as"""
    if 'impersonated_user_id' in session:
        return User.query.get(session['impersonated_user_id'])
    return get_current_user()
```

### **5. Security Requirements**
- Admins cannot impersonate other admins
- Users cannot impersonate themselves
- All impersonation activities must be logged
- Session validation on every request
- Proper error handling and status codes

### **6. Beginner-Friendly Code Style**
- Use simple, descriptive variable names
- Add lots of comments explaining what each part does
- Keep functions short and focused
- Use basic error handling (try/except)
- Simple password hashing (SHA256 for learning)
- Clear, readable code structure

### **7. Testing Requirements**
Create a test script that:
- Tests admin login
- Lists all users
- Starts impersonation
- Verifies dashboard shows impersonated user
- Stops impersonation
- Checks activity log

### **8. Sample Data**
Create these test users:
- `admin/admin123` (Administrator)
- `pratiksha/pratiksha123` (Regular user)
- `anand/anand123` (Regular user)
- `pallavi/pallavi123` (Regular user)

## **Expected File Structure**
```
task_7/
├── app.py              # Main Flask application
├── quick_test.py       # Test script
├── requirements.txt    # Dependencies
├── README.md          # Documentation
└── users.db           # SQLite database (auto-created)
```

## **Success Criteria**
✅ Admin can login and see list of users  
✅ Admin can impersonate regular users  
✅ Dashboard shows impersonated user info  
✅ Admin can stop impersonation  
✅ All activities are logged with timestamps  
✅ Security checks prevent admin-to-admin impersonation  
✅ Code is beginner-friendly and well-commented  
✅ Test script validates all functionality  

## **Key Learning Points**
- Flask session management
- User authentication and authorization
- Database relationships and logging
- Security considerations in impersonation
- RESTful API design
- Error handling and validation

This prompt creates a complete, working user impersonation system that demonstrates authentication bypass for administrators while maintaining proper security checks and activity logging.
