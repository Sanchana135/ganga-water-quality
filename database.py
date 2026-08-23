from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Researcher') # Administrator, Environmental Analyst, Researcher
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Station(db.Model):
    __tablename__ = 'stations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='ACTIVE') # ACTIVE, MAINTENANCE, INACTIVE
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    readings = db.relationship('SensorReading', backref='station', lazy=True, cascade="all, delete-orphan")
    wqi_logs = db.relationship('WaterQuality', backref='station', lazy=True, cascade="all, delete-orphan")
    forecasts = db.relationship('Forecast', backref='station', lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship('Alert', backref='station', lazy=True, cascade="all, delete-orphan")
    satellite_obs = db.relationship('SatelliteData', backref='station', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location': self.location,
            'status': self.status
        }

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ph = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False) # Celsius
    dissolved_oxygen = db.Column(db.Float, nullable=False) # mg/L
    turbidity = db.Column(db.Float, nullable=False) # NTU
    tds = db.Column(db.Float, nullable=False) # mg/L Total Dissolved Solids
    conductivity = db.Column(db.Float, nullable=False) # µS/cm
    bod = db.Column(db.Float, nullable=False) # mg/L Biological Oxygen Demand
    cod = db.Column(db.Float, nullable=False) # mg/L Chemical Oxygen Demand

    def to_dict(self):
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else f"Station #{self.station_id}",
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else '',
            'ph': round(self.ph, 2),
            'temperature': round(self.temperature, 2),
            'dissolved_oxygen': round(self.dissolved_oxygen, 2),
            'turbidity': round(self.turbidity, 2),
            'tds': round(self.tds, 2),
            'conductivity': round(self.conductivity, 2),
            'bod': round(self.bod, 2),
            'cod': round(self.cod, 2)
        }

class WaterQuality(db.Model):
    __tablename__ = 'water_quality'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    wqi = db.Column(db.Float, nullable=False)
    quality_category = db.Column(db.String(50), nullable=False) # Excellent, Good, Moderate, Poor, Critical
    pollution_risk = db.Column(db.String(50), nullable=False) # Low, Moderate, High, Severe

    def to_dict(self):
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else f"Station #{self.station_id}",
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else '',
            'wqi': round(self.wqi, 2),
            'quality_category': self.quality_category,
            'pollution_risk': self.pollution_risk
        }

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    forecast_time = db.Column(db.DateTime, nullable=False)
    horizon_hours = db.Column(db.Integer, nullable=False) # 6, 12, 24, 72
    predicted_wqi = db.Column(db.Float, nullable=False)
    predicted_category = db.Column(db.String(50), nullable=False)
    predicted_do = db.Column(db.Float, nullable=False)
    predicted_turbidity = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, default=92.5) # Percentage confidence indicator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else f"Station #{self.station_id}",
            'forecast_time': self.forecast_time.strftime('%Y-%m-%d %H:%M:%S') if self.forecast_time else '',
            'horizon_hours': self.horizon_hours,
            'predicted_wqi': round(self.predicted_wqi, 2),
            'predicted_category': self.predicted_category,
            'predicted_do': round(self.predicted_do, 2),
            'predicted_turbidity': round(self.predicted_turbidity, 2),
            'confidence': round(self.confidence, 1)
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)
    parameter = db.Column(db.String(50), nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False) # INFO, WARNING, HIGH, CRITICAL
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else f"Station #{self.station_id}",
            'alert_type': self.alert_type,
            'parameter': self.parameter,
            'current_value': round(self.current_value, 2),
            'threshold': round(self.threshold, 2),
            'message': self.message,
            'severity': self.severity,
            'resolved': self.resolved,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class SatelliteData(db.Model):
    __tablename__ = 'satellite_data'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    observation_date = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    satellite_index = db.Column(db.Float, nullable=False) # Normalized Difference Turbidity Index (NDTI)
    turbidity_proxy = db.Column(db.Float, nullable=False) # Remote sensed proxy NTU
    water_extent = db.Column(db.Float, nullable=False) # km2 river width/area
    ndvi_water = db.Column(db.Float, nullable=False) # Chlorophyll/Algae proxy
    raw_source = db.Column(db.String(100), default="Sentinel-2 MSIL2A / Landsat-9 Demo Proxy")

    def to_dict(self):
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else f"Station #{self.station_id}",
            'observation_date': self.observation_date.strftime('%Y-%m-%d') if self.observation_date else '',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'satellite_index': round(self.satellite_index, 4),
            'turbidity_proxy': round(self.turbidity_proxy, 2),
            'water_extent': round(self.water_extent, 2),
            'ndvi_water': round(self.ndvi_water, 4),
            'raw_source': self.raw_source
        }
