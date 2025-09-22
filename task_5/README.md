# Template-Based Export System ✅ WORKING

A simple Flask app demonstrating **template-based export functionality** for camera maintenance data.

## 🎯 **What This Does**

This system demonstrates the core task requirement:
- **Template-based exports**: Uses Jinja2 templates to format data
- **Multiple formats**: HTML and CSV exports using templates
- **Dynamic data**: Camera maintenance data passed into templates
- **API endpoints**: REST API to trigger exports and download files

## ✅ **Files Included**

- `simple_app.py` - Main Flask application (WORKING)
- `templates/simple_report.html` - HTML template for reports
- `templates/simple_report.csv` - CSV template for data export
- `test_simple.py` - Test script to verify everything works
- `requirements.txt` - Minimal dependencies (Flask, SQLAlchemy, requests)

## 🚀 **How to Run**

```bash
# 1. Set up virtual environment
python3 -m venv camera_env
source camera_env/bin/activate
pip install -r requirements.txt

# 2. Run the app
python3 simple_app.py

# 3. Test it works (in another terminal)
python3 test_simple.py
```

## 📋 **API Endpoints**

- `GET /` - Home page (shows system status)
- `GET /api/cameras` - List all cameras with data
- `GET /api/export/templates` - Available export templates
- `POST /api/export` - Create export using template
- `GET /api/download/<filename>` - Download generated file

## 🎨 **Template Examples**

**Create HTML Export:**
```bash
curl -X POST http://127.0.0.1:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"format": "html"}'
```

**Create CSV Export:**
```bash
curl -X POST http://127.0.0.1:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}'
```

## API Endpoints

### Get All Cameras
```
GET /api/cameras
```
Returns list of all cameras with their current status and latest predictions.

### Get Export Templates
```
GET /api/export/templates
```
Returns available export formats (HTML, CSV, Excel, and PDF if WeasyPrint is installed).

### Create Export
```
POST /api/export
Content-Type: application/json

{
  "format": "html",           // html, csv, excel, or pdf
  "camera_ids": [1, 2, 3],   // optional: specific cameras (default: all)
  "days_back": 30            // optional: how many days of data (default: 30)
}
```

### Download Export File
```
GET /api/download/<filename>
```

### Get Camera Predictions
```
GET /api/predictions/<camera_id>
```
Returns prediction history for a specific camera.

## Export Formats

### HTML Report
- Nice looking web page with styling
- Shows summary stats and detailed camera info
- Good for viewing in browser or sharing

### CSV File  
- Simple comma-separated values
- Easy to import into Excel or other tools
- Good for data analysis

### Excel Workbook
- Multiple sheets (Summary + Details)
- Formatted with headers and colors
- Good for business reports

### PDF Report (if WeasyPrint available)
- Same content as HTML but in PDF format
- Good for printing or official documents

## Example Usage

### Basic Export
```python
import requests

# Create HTML export of all cameras
response = requests.post('http://localhost:5000/api/export', json={
    'format': 'html'
})

if response.status_code == 200:
    result = response.json()
    print(f"Export created: {result['filename']}")
    
    # Download the file
    download_url = f"http://localhost:5000{result['download_url']}"
    file_response = requests.get(download_url)
    
    with open(result['filename'], 'wb') as f:
        f.write(file_response.content)
```

### Filtered Export
```python
# Export only specific cameras for last 60 days
response = requests.post('http://localhost:5000/api/export', json={
    'format': 'excel',
    'camera_ids': [1, 3, 5],
    'days_back': 60
})
```

## File Structure

```
task_4/
├── app.py                 # Main Flask application
├── models.py              # Database models (Camera, Maintenance, Predictions)
├── export_service.py      # Export logic and template rendering
├── api_routes.py          # API endpoint definitions
├── test_api.py           # Test script
├── requirements.txt       # Python dependencies
├── templates/            # Jinja2 templates for exports
│   ├── maintenance_report.html
│   └── maintenance_report.csv
├── exports/              # Generated export files (created automatically)
└── utils/
    └── sample_data.py    # Creates sample data for testing
```

## Templates

The system uses Jinja2 templates to format the export data:

- `templates/maintenance_report.html` - HTML report template
- `templates/maintenance_report.csv` - CSV export template

You can modify these templates to change how the reports look or add new fields.

## Performance Notes

- Exports are limited to 1000 cameras by default to prevent memory issues
- The system uses bulk database queries to improve performance
- For very large datasets, consider implementing background processing

## Troubleshooting

### "WeasyPrint not available" message
This is normal if you don't have WeasyPrint installed. PDF export will be disabled but everything else works fine.

### Database errors
Delete the `cameras.db` file and restart the app to recreate the database with fresh sample data.

### Port 5000 already in use
Change the port in `app.py`: `app.run(debug=True, port=5001)`

## Adding New Export Formats

To add a new export format:

1. Create a new template file in `templates/`
2. Add a new method to `ExportService` class
3. Update the `get_available_templates()` method
4. Add the format to the API route handler

## Sample Data

The system creates 5 sample cameras with:
- Random maintenance records
- AI predictions with different health statuses
- Realistic sensor data (temperature, humidity, etc.)

This gives you data to test the export functionality right away.

## Next Steps

- Add user authentication
- Implement real-time camera monitoring
- Add email notifications for critical predictions
- Create a web dashboard for viewing reports
- Add more export formats (JSON, XML, etc.)
