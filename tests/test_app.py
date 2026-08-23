"""
Unit and Integration Test Suite for Ganga River Water Quality DSS
"""

import os
import unittest
from app import create_app
from database import db, User, Station, SensorReading, WaterQuality, Alert
from services.water_quality import calculate_wqi
from services.recommendation_engine import generate_dss_recommendations

class GangaDSSTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            # Create test station
            st = Station(id=101, name="Haridwar Test Station", latitude=29.94, longitude=78.16, location="Upper Ganga", status="ACTIVE")
            db.session.add(st)

            # Create test admin user
            u = User(name="Test Admin", email="testadmin@ganga.gov.in", role="Administrator")
            u.set_password("Admin@123")
            db.session.add(u)
            
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_wqi_calculation(self):
        """Test standard WQI formula calculation."""
        # Clean water values
        res_clean = calculate_wqi(ph=7.2, do=9.2, turbidity=2.0, tds=120.0, bod=1.0, cod=3.0)
        self.assertLessEqual(res_clean['wqi'], 50.0)
        self.assertIn(res_clean['category'], ['Excellent', 'Good'])

        res_polluted = calculate_wqi(ph=8.8, do=2.5, turbidity=60.0, tds=650.0, bod=10.0, cod=35.0)
        self.assertGreater(res_polluted['wqi'], 75.0)
        self.assertIn(res_polluted['category'], ['Poor', 'Critical'])

    def test_user_authentication(self):
        """Test login, existing accounts, auto-registration, and invalid passwords."""
        # 1. Existing seeded admin account login
        res = self.client.post('/login', json={
            "email": "testadmin@ganga.gov.in",
            "password": "Admin@123"
        })
        self.assertEqual(res.status_code, 200)

        # 2. Existing account with wrong password (should fail)
        res_fail = self.client.post('/login', json={
            "email": "testadmin@ganga.gov.in",
            "password": "WrongPassword"
        })
        self.assertEqual(res_fail.status_code, 401)

        # 3. Invalid email format (should fail)
        res_invalid_email = self.client.post('/login', json={
            "email": "invalid-email-string",
            "password": "Password123"
        })
        self.assertEqual(res_invalid_email.status_code, 400)

        # 4. New email auto-registration on login
        new_email = "student.researcher@university.edu"
        res_auto = self.client.post('/login', json={
            "email": new_email,
            "password": "MySecretPassword123"
        })
        self.assertEqual(res_auto.status_code, 200)
        data = res_auto.get_json()
        self.assertEqual(data['user']['email'], new_email)
        self.assertEqual(data['user']['role'], 'Researcher') # Default role: Researcher

        # 5. Subsequent login for the newly auto-created account with correct password
        res_subsequent = self.client.post('/login', json={
            "email": new_email,
            "password": "MySecretPassword123"
        })
        self.assertEqual(res_subsequent.status_code, 200)

    def test_sensor_reading_simulation_api(self):
        """Test sensor reading ingestion API."""
        self.client.post('/login', json={"email": "testadmin@ganga.gov.in", "password": "Admin@123"})

        res = self.client.post('/api/readings/simulate', json={
            "station_id": 101,
            "ph": 7.5,
            "dissolved_oxygen": 7.2,
            "turbidity": 12.0,
            "tds": 220.0
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data['reading']['station_id'], 101)
        self.assertIn('wqi', data['water_quality'])

    def test_forecast_engine(self):
        """Test AI forecast prediction engine."""
        self.client.post('/login', json={"email": "testadmin@ganga.gov.in", "password": "Admin@123"})

        res = self.client.post('/api/forecast', json={
            "station_id": 101,
            "horizon_hours": 24,
            "rainfall_mm": 5.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('predicted_wqi', data['forecast'])
        self.assertIn('predicted_category', data['forecast'])

    def test_dss_recommendations(self):
        """Test Decision Support System recommendation engine."""
        advice = generate_dss_recommendations("Haridwar Test Station", {"ph": 7.2, "dissolved_oxygen": 2.8, "turbidity": 50.0}, {"wqi": 95.0, "category": "Poor", "pollution_risk": "High"})
        self.assertIn("Severe DO Depletion", advice['key_drivers'][0])
        self.assertTrue(len(advice['immediate_actions']) > 0)

if __name__ == '__main__':
    unittest.main()
