"""
Seed Data Generator for Ganga Water Quality Forecasting System
Initializes SQLite Database, populates stations, historical IoT sensor readings, WQI logs,
satellite observations, early warning alerts, seed users, and exports CSV datasets.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask
from config import Config
from database import db, User, Station, SensorReading, WaterQuality, Forecast, Alert, SatelliteData
from services.water_quality import calculate_wqi
from services.satellite_service import generate_satellite_observation

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_database():
    app = create_app()
    with app.app_context():
        print(f"Initializing database schema at {Config.DB_PATH}...")
        os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Safely drop and create all tables for a clean seed
        db.drop_all()
        db.create_all()

        print("Seeding demo users...")
        users = [
            User(name="System Administrator", email="admin@ganga.gov.in", role="Administrator"),
            User(name="Dr. Ananya Sharma", email="analyst@ganga.gov.in", role="Environmental Analyst"),
            User(name="Prof. Rajesh Kumar", email="researcher@ganga.gov.in", role="Researcher")
        ]
        users[0].set_password("Admin@123")
        users[1].set_password("Analyst@123")
        users[2].set_password("Research@123")

        for u in users:
            db.session.add(u)
        db.session.commit()
        print("Demo users seeded successfully.")

        print("Seeding Ganga river monitoring stations...")
        stations_data = Config.STATIONS
        stations = []
        for s in stations_data:
            st = Station(
                id=s['id'],
                name=s['name'],
                latitude=s['lat'],
                longitude=s['lng'],
                location=s['location'],
                status='ACTIVE'
            )
            db.session.add(st)
            stations.append(st)
        db.session.commit()
        print(f"Seeded {len(stations)} monitoring stations.")

        # Profiles for realistic sensor generation per station type
        profiles = {
            "Haridwar": {"ph": (7.3, 7.9), "do": (8.0, 9.5), "turb": (3.0, 14.0), "tds": (100, 200), "bod": (1.0, 2.2), "cod": (3.0, 8.0)},
            "Rishikesh": {"ph": (7.4, 8.0), "do": (8.2, 9.8), "turb": (2.0, 10.0), "tds": (90, 180), "bod": (0.8, 1.8), "cod": (2.5, 6.0)},
            "Kanpur": {"ph": (6.7, 8.6), "do": (3.2, 5.8), "turb": (25.0, 75.0), "tds": (380, 680), "bod": (5.0, 12.5), "cod": (18.0, 45.0)},
            "Prayagraj": {"ph": (7.1, 8.1), "do": (5.8, 7.4), "turb": (15.0, 40.0), "tds": (240, 420), "bod": (2.8, 5.2), "cod": (10.0, 22.0)},
            "Varanasi": {"ph": (7.0, 8.3), "do": (4.2, 6.4), "turb": (20.0, 58.0), "tds": (310, 520), "bod": (3.8, 8.8), "cod": (14.0, 32.0)},
            "Patna": {"ph": (7.1, 8.2), "do": (4.8, 6.8), "turb": (22.0, 52.0), "tds": (280, 490), "bod": (3.2, 7.2), "cod": (12.0, 28.0)}
        }

        print("Generating historical IoT sensor readings & WQI records...")
        now = datetime.utcnow()
        sensor_records = []
        satellite_records = []

        # Generate 100 historical readings per station over 25 days (every 6 hours)
        for st in stations:
            prof = profiles.get(st.name, profiles["Haridwar"])
            for step in range(100, 0, -1):
                timestamp = now - timedelta(hours=step * 6)
                
                ph = round(random.uniform(*prof['ph']), 2)
                temp = round(random.uniform(18.0, 28.5), 2)
                do = round(random.uniform(*prof['do']), 2)
                turb = round(random.uniform(*prof['turb']), 2)
                tds = round(random.uniform(*prof['tds']), 2)
                cond = round(tds * 1.56 + random.uniform(-10, 10), 2)
                bod = round(random.uniform(*prof['bod']), 2)
                cod = round(random.uniform(*prof['cod']), 2)

                sr = SensorReading(
                    station_id=st.id,
                    timestamp=timestamp,
                    ph=ph,
                    temperature=temp,
                    dissolved_oxygen=do,
                    turbidity=turb,
                    tds=tds,
                    conductivity=cond,
                    bod=bod,
                    cod=cod
                )
                db.session.add(sr)
                
                wqi_res = calculate_wqi(ph, do, turb, tds, bod, cod)
                wq = WaterQuality(
                    station_id=st.id,
                    timestamp=timestamp,
                    wqi=wqi_res['wqi'],
                    quality_category=wqi_res['category'],
                    pollution_risk=wqi_res['pollution_risk']
                )
                db.session.add(wq)

                sensor_records.append({
                    "station_id": st.id,
                    "station_name": st.name,
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "ph": ph, "temperature": temp, "dissolved_oxygen": do,
                    "turbidity": turb, "tds": tds, "conductivity": cond,
                    "bod": bod, "cod": cod, "wqi": wqi_res['wqi'],
                    "quality_category": wqi_res['category'],
                    "pollution_risk": wqi_res['pollution_risk']
                })

            # Satellite observations (1 per day for 15 days)
            for day in range(15, 0, -1):
                sat_date = now - timedelta(days=day)
                sat_data = generate_satellite_observation(st.id, st.latitude, st.longitude)
                sat_obj = SatelliteData(
                    station_id=st.id,
                    observation_date=sat_date,
                    latitude=st.latitude,
                    longitude=st.longitude,
                    satellite_index=sat_data['satellite_index'],
                    turbidity_proxy=sat_data['turbidity_proxy'],
                    water_extent=sat_data['water_extent'],
                    ndvi_water=sat_data['ndvi_water'],
                    raw_source=sat_data['raw_source']
                )
                db.session.add(sat_obj)
                satellite_records.append({
                    "station_id": st.id,
                    "station_name": st.name,
                    "observation_date": sat_date.strftime('%Y-%m-%d'),
                    "latitude": st.latitude,
                    "longitude": st.longitude,
                    "satellite_index": sat_data['satellite_index'],
                    "turbidity_proxy": sat_data['turbidity_proxy'],
                    "water_extent": sat_data['water_extent'],
                    "ndvi_water": sat_data['ndvi_water'],
                    "raw_source": sat_data['raw_source']
                })

        db.session.commit()
        print(f"Inserted {len(sensor_records)} sensor readings and {len(satellite_records)} satellite records.")

        print("Generating initial alerts...")
        alert_kanpur = Alert(
            station_id=3,
            alert_type="High Organic Pollution",
            parameter="BOD / COD",
            current_value=11.5,
            threshold=5.0,
            message="Kanpur station recorded elevated BOD (11.5 mg/L) indicating industrial/sewage inflow.",
            severity="HIGH",
            resolved=False,
            created_at=now - timedelta(hours=2)
        )
        alert_varanasi = Alert(
            station_id=5,
            alert_type="Elevated Turbidity Warning",
            parameter="Turbidity",
            current_value=54.2,
            threshold=35.0,
            message="Varanasi station recorded high turbidity (54.2 NTU) from upstream runoff.",
            severity="WARNING",
            resolved=False,
            created_at=now - timedelta(hours=5)
        )
        db.session.add(alert_kanpur)
        db.session.add(alert_varanasi)
        db.session.commit()

        print("Exporting seed CSV datasets to data/ folder...")
        df_all = pd.DataFrame(sensor_records)
        df_all.to_csv(os.path.join(Config.UPLOAD_FOLDER, 'demo_water_quality.csv'), index=False)
        df_all[['station_id', 'station_name', 'timestamp', 'ph', 'temperature', 'dissolved_oxygen', 'turbidity', 'tds', 'conductivity', 'bod', 'cod']].to_csv(
            os.path.join(Config.UPLOAD_FOLDER, 'demo_sensor_data.csv'), index=False
        )
        pd.DataFrame(satellite_records).to_csv(os.path.join(Config.UPLOAD_FOLDER, 'demo_satellite_data.csv'), index=False)
        print("CSV Datasets exported successfully.")

if __name__ == '__main__':
    seed_database()
