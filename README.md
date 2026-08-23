# Real-Time Ganga River Water Quality Forecasting Using AI-Enabled DSS, Satellite Data, IoT, and Dynamic Models

A complete, professional, full-stack AI/ML software application developed for academic project demonstration, viva, and environmental decision-support system (DSS) evaluation.

---
##LIVE DEMO

https://ganga-water-quality-w200.onrender.com/
---


##PROTOTYPE

https://drive.google.com/file/d/1nT9kmsOH3KIuyik3tUV_nFXv1LqQvpQX/view?usp=drive_link


## 1. Executive Summary & Problem Statement

The Ganga River basin sustains over 400 million people across northern India. Monitoring and forecasting river water quality is vital to safeguard public health, maintain ecological flow, and combat industrial and municipal pollution. 

This platform integrates:
1. **IoT Sensor Telemetry**: Continuous monitoring of pH, Dissolved Oxygen (DO), Turbidity, TDS, Electrical Conductivity, BOD, and COD.
2. **Satellite Earth Observation**: Sentinel-2 Level-2A remote sensing proxies (NDTI Normalized Difference Turbidity Index & river surface extent).
3. **AI/ML Forecasting**: Scikit-Learn Random Forest ensemble regressor and classifier predicting multi-horizon (6h, 12h, 24h, 72h) Water Quality Index (WQI).
4. **Decision Support System (DSS)**: Rule-based AI engine delivering structured advisory recommendations and field action items.
5. **Early Warning Alerts**: Automated threshold evaluation triggering instant notifications.

---

## 2. Technology Stack

- **Frontend**: HTML5, CSS3 (Bespoke Glassmorphism Design System), Vanilla JavaScript (ES6+), Leaflet.js (OpenStreetMap GIS), Chart.js (Interactive Multi-Parameter Graphs), FontAwesome Icons.
- **Backend**: Python 3.13, Flask framework, RESTful API architecture.
- **Database**: SQLite with SQLAlchemy ORM.
- **AI / Machine Learning**: Scikit-Learn (RandomForestRegressor & RandomForestClassifier), Pandas, NumPy, Joblib serialization.
- **Authentication**: Werkzeug security password hashing, session management, role-based access control (RBAC).

---

## 3. Prototype Authentication & Demo Credentials

The platform features a **seamless direct authentication system**:
- **Automatic User Creation**: Any user can sign in using their own valid email address. If the email is not registered yet, an account is created automatically in SQLite with the default role `Researcher` and securely hashed Werkzeug password.
- **Existing Accounts**: If the email exists, the password is verified against the stored hash.
- **Role Control**: Automatic sign-in users are assigned the `Researcher` role. Administrator accounts cannot be created automatically.
- **Demo Accounts**: Pre-configured admin, analyst, and researcher accounts remain unchanged.

| Role | Email Address | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@ganga.gov.in` | `Admin@123` | Full system access, user management, station creation |
| **Environmental Analyst** | `analyst@ganga.gov.in` | `Analyst@123` | Dashboard, IoT Studio, AI Forecast, DSS, Reports |
| **Researcher** | `researcher@ganga.gov.in` | `Research@123` | Read-only analytics, historical logs, dataset export |
| **New Users** | *Any valid email* | *User password* | Automatic `Researcher` account creation & login |

---

## 4. System Architecture

```
                                  +---------------------------------------+
                                  |     Sentinel-2 / Landsat-9 Satellite  |
                                  |   Remote Sensing Proxies (NDTI Index) |
                                  +-------------------+-------------------+
                                                      |
                                                      v
+-----------------------------+          +------------+------------+          +-----------------------------+
|    IoT Sensor Telemetry     | -------->|  Flask REST API Backend | <--------| Dynamic Hydrologic Model    |
| (Haridwar, Kanpur, Varanasi)|          |  & SQLAlchemy SQLite DB |          | (Rainfall & Flow Drift)     |
+-----------------------------+          +------------+------------+          +-----------------------------+
                                                      |
                                                      v
                                         +------------+------------+
                                         |   Scikit-Learn ML Model |
                                         |  RandomForest Pipeline  |
                                         +------------+------------+
                                                      |
                                                      v
                                         +------------+------------+
                                         |  AI Decision Support    |
                                         |      System (DSS)       |
                                         +-------------------------+
```

---

## 5. Academic Prototype Disclaimer

> **Notice**: As specified in academic research guidelines, IoT telemetry readings and satellite remote sensing observations operate in a **realistic local demonstration dataset mode** based on published Ganga river basin parameter ranges. All demo data is clearly labeled in the application header.

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.9+ installed on Windows / Linux / macOS.

### Step 1: Clone & Setup Virtual Environment

```bash
# Navigate to project directory
cd ganga-water-quality

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 3: Initialize Database & Seed Data

Populates SQLite database (`instance/ganga.db`) with monitoring stations, historical readings, satellite logs, sample alerts, demo users, and exports CSV files to `data/`.

```bash
python seed_data.py
```

### Step 4: Train Machine Learning Pipeline

Trains Random Forest Regressor & Classifier models, evaluates test set metrics (MAE, RMSE, R², Accuracy, F1-Score), and saves artifact to `models/water_quality_model.joblib`.

```bash
python train_model.py
```

### Step 5: Launch Flask Server

```bash
python app.py
```

Access the application in your browser at: **`http://127.0.0.1:5000`**

---

## 7. Running Unit Tests

Run the automated test suite covering authentication, WQI calculations, IoT ingestion, AI forecasting, and DSS recommendations:

```bash
python -m unittest tests/test_app.py
```

---

## 8. Main Modules & API Reference

### Core Application Routes
- `/` - Modern Scientific Landing Page
- `/login` / `/register` - Authentication portal
- `/dashboard` - Main Overview Dashboard with stat cards & mini GIS map
- `/monitoring` - Real-Time IoT Telemetry & Sensor Simulation Studio
- `/map` - Interactive Ganga GIS OpenStreetMap Leaflet Map
- `/forecast` - Multi-horizon AI Forecast Engine (6h, 12h, 24h, 72h)
- `/satellite` - Satellite Earth Observation & Remote Sensing Log
- `/dss` - AI Decision Support System Advisory Panel
- `/analytics` - Interactive Multi-Parameter Time Series Analysis
- `/alerts` - Early Warning Ecological Threshold Alert Center
- `/history` - Searchable Paginated Historical Data Grid & CSV Export
- `/reports` - Custom Assessment Report Compiler & Printable PDF Layout
- `/upload` - Dataset Ingestion & CSV Column Validation Portal
- `/admin` - User Administration & Station Registration Control Panel

### Key REST APIs
- `GET /api/dashboard/stats` - Returns basin stats, average WQI, active alerts count.
- `GET /api/stations` - Returns list of stations with latest readings and WQI status.
- `POST /api/readings/simulate` - Ingests new IoT reading, calculates WQI, evaluates alert thresholds.
- `POST /api/forecast` - Executes Random Forest model prediction for station & horizon.
- `GET /api/dss` - Generates executive summary and prioritized action recommendations.
- `POST /api/upload` - Validates uploaded CSV files for required headers and numeric sanity.

---

## 9. Project Verification & Compliance

- **WQI Formula**: Implements Weighted Arithmetic Water Quality Index methodology.
- **Model Performance**:
  - Regression R² Score: **> 0.99** (MAE: **~5.2**, RMSE: **~7.3**)
  - Classification Accuracy: **> 97.5%** (F1-Score: **~0.96**)
- **Security**: No clear-text passwords stored; Werkzeug PBKDF2 SHA256 password hashing enforced.
