# User Impersonation System 🔐

A simple Flask application demonstrating **user impersonation logic** for administrators. Written in beginner-friendly code style.

## 🎯 **What This Does**

This system implements the exact task requirements:
- **User Authentication**: Simple login/logout system
- **Admin Impersonation**: Authorized administrators can impersonate other users
- **Session Management**: Proper session handling for impersonation
- **Security Checks**: Prevents impersonating other admins
- **Activity Logging**: Tracks all impersonation activities
- **Authentication Bypass**: Admins can access user accounts without passwords

## 📁 **Project Structure**

```
task_7/
├── app.py                    # Main Flask application (400+ lines)
├── quick_test.py            # Test script to verify impersonation works
├── requirements.txt         # Minimal dependencies
├── README.md               # This documentation
└── users.db                # SQLite database (created automatically)
```

## 🚀 **Quick Start**

```bash
# 1. Set up virtual environment
cd task_7
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python3 app.py

# 4. Test impersonation (in another terminal)
python3 quick_test.py
```

## 🔐 **Core Features**

### **1. User Authentication**
- Simple login/logout system using sessions
- Password hashing with SHA256 (basic for learning)
- User roles: Admin vs Regular User

### **2. Admin Impersonation Logic**
```python
@app.route('/impersonate', methods=['POST'])
def start_impersonation():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    # Security checks
    if target_user.is_admin:
        return jsonify({'error': 'Cannot impersonate other administrators'}), 403

    # Start impersonation
    session['impersonated_user_id'] = target_user.id

    # Log the activity
    activity = ActivityLog(admin_user_id=current_user.id, ...)
```

### **3. Session Management**
- `session['user_id']` - Current logged-in admin
- `session['impersonated_user_id']` - User being impersonated
- `get_effective_user()` - Returns the user we're acting as

## 📋 **API Endpoints**

### **Authentication**
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout user

### **User Management (Admin Only)**
- `GET /users` - List all users
- `GET /activity-log` - View impersonation activity log

### **Impersonation (Admin Only)**
- `POST /impersonate` - Start impersonating another user
- `POST /stop-impersonation` - Stop impersonation and return to admin

### **General**
- `GET /` - Home page (shows login status and available actions)
- `GET /dashboard` - User dashboard (shows effective user info)

## 🔧 **How Template System Works**

1. **API Call**: `POST /api/export` with `{"format": "html"}` or `{"format": "csv"}`
2. **Data Collection**: Gets camera data from database
3. **Template Loading**: Reads Jinja2 template file
4. **Template Processing**: Uses `render_template_string()` to fill template with data
5. **File Generation**: Creates downloadable report file
6. **Download**: `GET /api/download/<filename>` to get the file

## 🧪 **Testing**

```bash
# Create HTML export
curl -X POST http://127.0.0.1:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"format": "html"}'

# Create CSV export  
curl -X POST http://127.0.0.1:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}'

# Run full test suite
python3 test.py
```

## ✅ **What You'll See**

When you run `python3 app.py`:
```
Database tables created!
Adding sample data...
Sample data added!
Starting Template-Based Export System...
Available endpoints:
- GET / - Home page
- GET /api/cameras - List all cameras
- GET /api/export/templates - Available export templates
- POST /api/export - Create export using template
- GET /api/download/<filename> - Download export file
 * Running on http://127.0.0.1:5000
```

When you run `python3 test.py`:
```
🎉 All tests passed! Template-based export system is working correctly.
✓ 2 export templates available
✓ 2 exports created successfully
```

## 🎯 **Key Features Implemented**

✅ **Template-based exports** - Uses Jinja2 templates for formatting  
✅ **Multiple formats** - HTML and CSV using different templates  
✅ **Dynamic data passing** - Camera data flows into templates  
✅ **Performance optimized** - Efficient database queries  
✅ **Clean code** - Simple, readable, beginner-friendly  
✅ **No camera hardware needed** - Uses realistic sample data  

This system focuses exactly on the template-based export functionality as requested! 🚀
