import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, 'instance', 'ganga.db'))

class Config:
    BASE_DIR = BASE_DIR
    DB_PATH = DB_PATH
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ganga-dss-secret-key-2026-secure-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{DB_PATH.replace('\\', '/')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, 'models', 'water_quality_model.joblib'))
    UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, 'data'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit
    
    # Ganga Stations default metadata
    STATIONS = [
        {"id": 1, "name": "Haridwar", "lat": 29.9457, "lng": 78.1642, "location": "Upper Ganga Basin, Uttarakhand"},
        {"id": 2, "name": "Rishikesh", "lat": 30.0869, "lng": 78.2676, "location": "Upper Ganga Basin, Uttarakhand"},
        {"id": 3, "name": "Kanpur", "lat": 26.4499, "lng": 80.3319, "location": "Middle Ganga Basin, Uttar Pradesh"},
        {"id": 4, "name": "Prayagraj", "lat": 25.4358, "lng": 81.8463, "location": "Triveni Sangam, Uttar Pradesh"},
        {"id": 5, "name": "Varanasi", "lat": 25.3176, "lng": 83.0061, "location": "Middle Ganga Basin, Uttar Pradesh"},
        {"id": 6, "name": "Patna", "lat": 25.5941, "lng": 85.1376, "location": "Lower Ganga Basin, Bihar"}
    ]
