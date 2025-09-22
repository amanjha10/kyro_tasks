# Camera Maintenance Export System
# Focus: Template-based export functionality

from flask import Flask, jsonify, request, send_file, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random

# Create Flask app
app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cameras.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create exports directory
if not os.path.exists('exports'):
    os.makedirs('exports')

# Simple Camera model
class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Active')
    installation_date = db.Column(db.DateTime, default=datetime.now)
    last_maintenance = db.Column(db.DateTime)

# Simple Maintenance Record model
class MaintenanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    maintenance_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    performed_date = db.Column(db.DateTime, default=datetime.now)
    technician = db.Column(db.String(100))

# Simple Prediction model
class PredictiveAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    prediction_status = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    predicted_failure_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'Camera Maintenance System is running!',
        'status': 'OK',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/cameras')
def get_cameras():
    cameras = Camera.query.all()
    camera_list = []
    
    for camera in cameras:
        # Get latest prediction
        latest_prediction = PredictiveAnalysis.query.filter_by(camera_id=camera.id).order_by(PredictiveAnalysis.created_at.desc()).first()
        
        camera_data = {
            'id': camera.id,
            'camera_id': camera.camera_id,
            'location': camera.location,
            'model': camera.model,
            'status': camera.status,
            'installation_date': camera.installation_date.strftime('%Y-%m-%d') if camera.installation_date else None,
            'last_maintenance': camera.last_maintenance.strftime('%Y-%m-%d') if camera.last_maintenance else 'Never',
            'latest_prediction': {
                'status': latest_prediction.prediction_status if latest_prediction else 'No prediction',
                'confidence': latest_prediction.confidence_score if latest_prediction else 0,
                'created_at': latest_prediction.created_at.strftime('%Y-%m-%d') if latest_prediction else None
            } if latest_prediction else None
        }
        camera_list.append(camera_data)
    
    return jsonify({
        'cameras': camera_list,
        'total': len(camera_list)
    })

@app.route('/api/export/templates')
def get_templates():
    """Get available export templates"""
    templates = [
        {'name': 'html', 'description': 'HTML Report (using template)'},
        {'name': 'csv', 'description': 'CSV File (using template)'},
    ]
    return jsonify({'templates': templates})

@app.route('/api/export', methods=['POST'])
def create_export():
    """Create export using selected template"""
    data = request.get_json()
    format_type = data.get('format', 'html')

    if format_type == 'html':
        return create_html_export()
    elif format_type == 'csv':
        return create_csv_export()
    else:
        return jsonify({'error': 'Unsupported format. Use html or csv'}), 400

def create_html_export():
    """Create HTML export using template"""
    cameras = Camera.query.all()

    # Read HTML template
    with open('templates/simple_report.html', 'r') as f:
        template_content = f.read()

    # Prepare data for template
    camera_data = []
    for camera in cameras:
        camera_data.append({
            'camera_id': camera.camera_id,
            'location': camera.location,
            'model': camera.model,
            'status': camera.status,
            'last_maintenance': camera.last_maintenance.strftime('%Y-%m-%d') if camera.last_maintenance else 'Never'
        })

    # Render template with data
    html_content = render_template_string(template_content,
                                        cameras=camera_data,
                                        generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join('exports', filename)

    with open(filepath, 'w') as f:
        f.write(html_content)

    return jsonify({
        'message': 'HTML export created using template',
        'filename': filename,
        'download_url': f'/api/download/{filename}'
    })

def create_csv_export():
    """Create CSV export using template"""
    cameras = Camera.query.all()

    # Read CSV template
    with open('templates/simple_report.csv', 'r') as f:
        template_content = f.read()

    # Prepare data for template
    camera_data = []
    for camera in cameras:
        camera_data.append({
            'camera_id': camera.camera_id,
            'location': camera.location,
            'model': camera.model,
            'status': camera.status,
            'last_maintenance': camera.last_maintenance.strftime('%Y-%m-%d') if camera.last_maintenance else 'Never'
        })

    # Render template with data
    csv_content = render_template_string(template_content, cameras=camera_data)

    filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('exports', filename)

    with open(filepath, 'w') as f:
        f.write(csv_content)

    return jsonify({
        'message': 'CSV export created using template',
        'filename': filename,
        'download_url': f'/api/download/{filename}'
    })



@app.route('/api/download/<filename>')
def download_file(filename):
    filepath = os.path.join('exports', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

def create_sample_data():
    """Create some sample cameras and data"""
    sample_cameras = [
        {'camera_id': 'CAM-001', 'location': 'Main Entrance', 'model': 'Sony XYZ-123'},
        {'camera_id': 'CAM-002', 'location': 'Parking Lot A', 'model': 'Canon ABC-456'},
        {'camera_id': 'CAM-003', 'location': 'Reception Area', 'model': 'Hikvision DEF-789'},
        {'camera_id': 'CAM-004', 'location': 'Loading Dock', 'model': 'Dahua GHI-012'},
        {'camera_id': 'CAM-005', 'location': 'Server Room', 'model': 'Axis JKL-345'},
    ]
    
    for cam_data in sample_cameras:
        camera = Camera(
            camera_id=cam_data['camera_id'],
            location=cam_data['location'],
            model=cam_data['model'],
            status=random.choice(['Active', 'Maintenance', 'Warning']),
            installation_date=datetime.now() - timedelta(days=random.randint(30, 365)),
            last_maintenance=datetime.now() - timedelta(days=random.randint(1, 90))
        )
        db.session.add(camera)
    
    db.session.commit()
    
    # Add some maintenance records and predictions
    cameras = Camera.query.all()
    for camera in cameras:
        # Add maintenance record
        maintenance = MaintenanceRecord(
            camera_id=camera.id,
            maintenance_type=random.choice(['Lens Cleaning', 'Firmware Update', 'Hardware Check']),
            description='Routine maintenance performed',
            performed_date=datetime.now() - timedelta(days=random.randint(1, 30)),
            technician='Tech Team'
        )
        db.session.add(maintenance)
        
        # Add prediction
        prediction = PredictiveAnalysis(
            camera_id=camera.id,
            prediction_status=random.choice(['Good', 'Warning', 'Critical']),
            confidence_score=random.uniform(0.7, 0.99),
            predicted_failure_date=datetime.now() + timedelta(days=random.randint(30, 180)),
            created_at=datetime.now() - timedelta(days=random.randint(1, 7))
        )
        db.session.add(prediction)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
        
        if Camera.query.count() == 0:
            print("Adding sample data...")
            create_sample_data()
            print("Sample data added!")
    
    print("Starting Flask app...")
    print("Available endpoints:")
    print("- GET / - Home page")
    print("- GET /api/cameras - List all cameras")
    print("- GET /api/export/templates - Available export formats")
    print("- POST /api/export - Create export (JSON: {'format': 'html|csv|excel'})")
    print("- GET /api/download/<filename> - Download export file")
    
    app.run(debug=True, port=5000)
