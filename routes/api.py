"""
REST API Blueprint
Exposes JSON endpoints for Dashboard, IoT Simulation, Map GIS, Forecast Engine,
Alerts, Satellite Proxies, Analytics, Searchable History, and Data Upload.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request, session, current_app
from database import db, Station, SensorReading, WaterQuality, Forecast, Alert, SatelliteData, User
from routes.auth import login_required, admin_required
from services.water_quality import calculate_wqi
from services.forecast_engine import forecast_engine
from services.alert_engine import evaluate_reading_alerts
from services.satellite_service import get_satellite_summary, generate_satellite_observation
from services.recommendation_engine import generate_dss_recommendations

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    stations = Station.query.all()
    total_stations = len(stations)
    
    # Latest reading per station
    latest_readings = []
    wqi_scores = []
    categories = {"Excellent": 0, "Good": 0, "Moderate": 0, "Poor": 0, "Critical": 0}
    
    for st in stations:
        last_r = SensorReading.query.filter_by(station_id=st.id).order_by(SensorReading.timestamp.desc()).first()
        last_wq = WaterQuality.query.filter_by(station_id=st.id).order_by(WaterQuality.timestamp.desc()).first()
        
        if last_r and last_wq:
            wqi_scores.append(last_wq.wqi)
            cat = last_wq.quality_category
            categories[cat] = categories.get(cat, 0) + 1
            latest_readings.append({
                "station_id": st.id,
                "station_name": st.name,
                "lat": st.latitude,
                "lng": st.longitude,
                "location": st.location,
                "timestamp": last_r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "ph": last_r.ph,
                "temperature": last_r.temperature,
                "dissolved_oxygen": last_r.dissolved_oxygen,
                "turbidity": last_r.turbidity,
                "tds": last_r.tds,
                "bod": last_r.bod,
                "cod": last_r.cod,
                "wqi": last_wq.wqi,
                "quality_category": last_wq.quality_category,
                "pollution_risk": last_wq.pollution_risk
            })

    avg_wqi = round(sum(wqi_scores) / len(wqi_scores), 2) if wqi_scores else 45.0
    
    if avg_wqi <= 25.0:
        overall_status = "EXCELLENT"
    elif avg_wqi <= 50.0:
        overall_status = "GOOD"
    elif avg_wqi <= 75.0:
        overall_status = "MODERATE"
    elif avg_wqi <= 100.0:
        overall_status = "POOR"
    else:
        overall_status = "CRITICAL"

    active_alerts = Alert.query.filter_by(resolved=False).order_by(Alert.created_at.desc()).limit(10).all()

    return jsonify({
        "total_stations": total_stations,
        "avg_wqi": avg_wqi,
        "overall_status": overall_status,
        "category_counts": categories,
        "latest_readings": latest_readings,
        "recent_alerts": [a.to_dict() for a in active_alerts],
        "system_mode": "Prototype / Simulated IoT & Satellite Data Mode"
    })

@api_bp.route('/stations', methods=['GET'])
@login_required
def get_stations():
    stations = Station.query.order_by(Station.id).all()
    result = []
    for st in stations:
        last_r = SensorReading.query.filter_by(station_id=st.id).order_by(SensorReading.timestamp.desc()).first()
        last_wq = WaterQuality.query.filter_by(station_id=st.id).order_by(WaterQuality.timestamp.desc()).first()
        data = st.to_dict()
        if last_r and last_wq:
            data.update({
                "last_updated": last_r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "ph": last_r.ph,
                "temperature": last_r.temperature,
                "dissolved_oxygen": last_r.dissolved_oxygen,
                "turbidity": last_r.turbidity,
                "tds": last_r.tds,
                "bod": last_r.bod,
                "cod": last_r.cod,
                "wqi": last_wq.wqi,
                "quality_category": last_wq.quality_category,
                "pollution_risk": last_wq.pollution_risk
            })
        result.append(data)
    return jsonify(result)

@api_bp.route('/stations/<int:station_id>', methods=['GET'])
@login_required
def get_station_detail(station_id):
    st = Station.query.get_or_404(station_id)
    readings = SensorReading.query.filter_by(station_id=station_id).order_by(SensorReading.timestamp.desc()).limit(50).all()
    wqi_logs = WaterQuality.query.filter_by(station_id=station_id).order_by(WaterQuality.timestamp.desc()).limit(50).all()
    sat_logs = SatelliteData.query.filter_by(station_id=station_id).order_by(SatelliteData.observation_date.desc()).limit(15).all()

    last_r = readings[0] if readings else None
    last_wq = wqi_logs[0] if wqi_logs else None

    dss_advice = generate_dss_recommendations(
        st.name, 
        last_r.to_dict() if last_r else {}, 
        last_wq.to_dict() if last_wq else {"wqi": 45, "category": "Good", "pollution_risk": "Low"}
    )

    return jsonify({
        "station": st.to_dict(),
        "latest_reading": last_r.to_dict() if last_r else None,
        "latest_wqi": last_wq.to_dict() if last_wq else None,
        "historical_readings": [r.to_dict() for r in readings],
        "satellite_observations": [s.to_dict() for s in sat_logs],
        "dss_recommendations": dss_advice
    })

@api_bp.route('/readings/simulate', methods=['POST'])
@login_required
def simulate_sensor_reading():
    """
    IoT Monitoring Simulation Trigger.
    Generates realistic sensor reading, computes WQI, evaluates alert rules,
    and updates database.
    """
    data = request.get_json() or {}
    station_id = data.get('station_id', 3) # Default Kanpur
    st = Station.query.get_or_404(station_id)

    # Custom parameter overrides or random generator
    if 'ph' in data and data['ph']:
        ph = float(data['ph'])
        temp = float(data.get('temperature', 24.5))
        do = float(data.get('dissolved_oxygen', 5.2))
        turb = float(data.get('turbidity', 22.0))
        tds = float(data.get('tds', 350.0))
        cond = float(data.get('conductivity', tds * 1.56))
        bod = float(data.get('bod', 4.5))
        cod = float(data.get('cod', 14.0))
    else:
        # Generate realistic random variations around station baseline
        last_r = SensorReading.query.filter_by(station_id=station_id).order_by(SensorReading.timestamp.desc()).first()
        base_ph = last_r.ph if last_r else 7.4
        base_do = last_r.dissolved_oxygen if last_r else 6.2
        base_turb = last_r.turbidity if last_r else 18.0
        base_tds = last_r.tds if last_r else 320.0
        base_bod = last_r.bod if last_r else 3.5
        base_cod = last_r.cod if last_r else 12.0

        ph = round(max(5.5, min(9.5, base_ph + random.uniform(-0.4, 0.4))), 2)
        temp = round(random.uniform(20.0, 29.0), 2)
        do = round(max(1.0, min(12.0, base_do + random.uniform(-0.6, 0.6))), 2)
        turb = round(max(2.0, min(120.0, base_turb + random.uniform(-5.0, 6.0))), 2)
        tds = round(max(80.0, min(800.0, base_tds + random.uniform(-15.0, 20.0))), 2)
        cond = round(tds * 1.56, 2)
        bod = round(max(0.5, min(20.0, base_bod + random.uniform(-0.8, 1.0))), 2)
        cod = round(max(2.0, min(60.0, base_cod + random.uniform(-2.0, 2.5))), 2)

    now = datetime.utcnow()
    new_reading = SensorReading(
        station_id=st.id,
        timestamp=now,
        ph=ph,
        temperature=temp,
        dissolved_oxygen=do,
        turbidity=turb,
        tds=tds,
        conductivity=cond,
        bod=bod,
        cod=cod
    )
    db.session.add(new_reading)
    
    wqi_res = calculate_wqi(ph, do, turb, tds, bod, cod)
    new_wq = WaterQuality(
        station_id=st.id,
        timestamp=now,
        wqi=wqi_res['wqi'],
        quality_category=wqi_res['category'],
        pollution_risk=wqi_res['pollution_risk']
    )
    db.session.add(new_wq)
    db.session.commit()

    # Trigger alert evaluation
    alerts_created = evaluate_reading_alerts(st.id, st.name, new_reading, wqi_res)

    return jsonify({
        "message": f"New IoT sensor reading recorded for {st.name}",
        "reading": new_reading.to_dict(),
        "water_quality": new_wq.to_dict(),
        "alerts_triggered": alerts_created
    }), 201

@api_bp.route('/forecast', methods=['POST'])
@login_required
def get_forecast():
    """
    Executes AI prediction pipeline for specified station and horizon.
    """
    data = request.get_json() or {}
    station_id = int(data.get('station_id', 3))
    horizon_hours = int(data.get('horizon_hours', 24)) # 6, 12, 24, 72
    rainfall_mm = float(data.get('rainfall_mm', 0.0))

    st = Station.query.get_or_404(station_id)
    last_r = SensorReading.query.filter_by(station_id=station_id).order_by(SensorReading.timestamp.desc()).first()
    last_wq = WaterQuality.query.filter_by(station_id=station_id).order_by(WaterQuality.timestamp.desc()).first()

    current_params = last_r.to_dict() if last_r else {
        "ph": 7.4, "temperature": 24.0, "dissolved_oxygen": 6.2, 
        "turbidity": 18.0, "tds": 320.0, "conductivity": 500.0, "bod": 3.5, "cod": 12.0
    }

    pred_res = forecast_engine.predict_horizon(station_id, current_params, horizon_hours, rainfall_mm)

    # Save forecast record in DB
    fc_obj = Forecast(
        station_id=station_id,
        forecast_time=datetime.strptime(pred_res['forecast_time'], '%Y-%m-%d %H:%M:%S'),
        horizon_hours=horizon_hours,
        predicted_wqi=pred_res['predicted_wqi'],
        predicted_category=pred_res['predicted_category'],
        predicted_do=pred_res['predicted_do'],
        predicted_turbidity=pred_res['predicted_turbidity'],
        confidence=pred_res['confidence']
    )
    db.session.add(fc_obj)
    db.session.commit()

    # Build historical trajectory for Chart.js (Past 24h -> Current -> Forecast)
    past_readings = SensorReading.query.filter_by(station_id=station_id).order_by(SensorReading.timestamp.desc()).limit(8).all()
    past_readings.reverse()

    trajectory = []
    for r in past_readings:
        wq = WaterQuality.query.filter_by(station_id=station_id, timestamp=r.timestamp).first()
        trajectory.append({
            "timestamp": r.timestamp.strftime('%H:%M (%d %b)'),
            "wqi": wq.wqi if wq else 50.0,
            "do": r.dissolved_oxygen,
            "turbidity": r.turbidity,
            "type": "historical"
        })

    # Add forecast point
    trajectory.append({
        "timestamp": f"+{horizon_hours}h ({datetime.strptime(pred_res['forecast_time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')})",
        "wqi": pred_res['predicted_wqi'],
        "do": pred_res['predicted_do'],
        "turbidity": pred_res['predicted_turbidity'],
        "type": "forecast"
    })

    return jsonify({
        "station": st.to_dict(),
        "current": {
            "timestamp": last_r.timestamp.strftime('%Y-%m-%d %H:%M:%S') if last_r else '',
            "wqi": last_wq.wqi if last_wq else 50.0,
            "category": last_wq.quality_category if last_wq else "Good",
            "do": last_r.dissolved_oxygen if last_r else 6.5,
            "turbidity": last_r.turbidity if last_r else 15.0
        },
        "forecast": pred_res,
        "trajectory": trajectory,
        "model_metrics": forecast_engine.metrics
    })

@api_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    severity = request.args.get('severity')
    station_id = request.args.get('station_id')
    resolved = request.args.get('resolved')

    query = Alert.query
    if severity:
        query = query.filter_by(severity=severity.upper())
    if station_id:
        query = query.filter_by(station_id=int(station_id))
    if resolved is not None:
        is_res = resolved.lower() in ['true', '1']
        query = query.filter_by(resolved=is_res)

    alerts = query.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])

@api_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    alt = Alert.query.get_or_404(alert_id)
    alt.resolved = True
    db.session.commit()
    return jsonify({"message": f"Alert #{alert_id} marked as resolved.", "alert": alt.to_dict()})

@api_bp.route('/satellite', methods=['GET'])
@login_required
def get_satellite_data():
    station_id = request.args.get('station_id')
    query = SatelliteData.query
    if station_id:
        query = query.filter_by(station_id=int(station_id))
    
    obs = query.order_by(SatelliteData.observation_date.desc()).all()
    summary = get_satellite_summary(station_id)
    
    return jsonify({
        "metadata": summary,
        "observations": [s.to_dict() for s in obs]
    })

@api_bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics_data():
    station_id = request.args.get('station_id')
    days = int(request.args.get('days', 30))

    query = SensorReading.query
    if station_id and station_id != 'all':
        query = query.filter_by(station_id=int(station_id))
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    readings = query.filter(SensorReading.timestamp >= cutoff).order_by(SensorReading.timestamp.asc()).all()

    timestamps = []
    ph_list = []
    do_list = []
    turb_list = []
    temp_list = []
    wqi_list = []

    for r in readings:
        wq = WaterQuality.query.filter_by(station_id=r.station_id, timestamp=r.timestamp).first()
        timestamps.append(r.timestamp.strftime('%d %b %H:%M'))
        ph_list.append(r.ph)
        do_list.append(r.dissolved_oxygen)
        turb_list.append(r.turbidity)
        temp_list.append(r.temperature)
        wqi_list.append(wq.wqi if wq else 50.0)

    return jsonify({
        "timestamps": timestamps,
        "ph": ph_list,
        "dissolved_oxygen": do_list,
        "turbidity": turb_list,
        "temperature": temp_list,
        "wqi": wqi_list
    })

@api_bp.route('/history', methods=['GET'])
@login_required
def get_history_table():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    station_id = request.args.get('station_id')
    search = request.args.get('search', '').strip()

    query = SensorReading.query.join(Station)

    if station_id and station_id != 'all':
        query = query.filter(SensorReading.station_id == int(station_id))

    if search:
        query = query.filter(Station.name.ilike(f'%{search}%'))

    pagination = query.order_by(SensorReading.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    rows = []
    for r in pagination.items:
        wq = WaterQuality.query.filter_by(station_id=r.station_id, timestamp=r.timestamp).first()
        row_dict = r.to_dict()
        row_dict['wqi'] = wq.wqi if wq else 50.0
        row_dict['quality_category'] = wq.quality_category if wq else 'Good'
        row_dict['pollution_risk'] = wq.pollution_risk if wq else 'Low'
        rows.append(row_dict)

    return jsonify({
        "items": rows,
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
        "per_page": per_page
    })

@api_bp.route('/dss', methods=['GET'])
@login_required
def get_dss():
    station_id = request.args.get('station_id', 3)
    st = Station.query.get_or_404(station_id)
    
    last_r = SensorReading.query.filter_by(station_id=st.id).order_by(SensorReading.timestamp.desc()).first()
    last_wq = WaterQuality.query.filter_by(station_id=st.id).order_by(WaterQuality.timestamp.desc()).first()
    
    dss_data = generate_dss_recommendations(
        st.name,
        last_r.to_dict() if last_r else {},
        last_wq.to_dict() if last_wq else {"wqi": 45, "category": "Good", "pollution_risk": "Low"}
    )
    return jsonify(dss_data)

@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_dataset():
    """
    Validates CSV file uploads for water quality, IoT readings, or Satellite observations.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    dataset_type = request.form.get('dataset_type', 'water_quality')

    if file.filename == '':
        return jsonify({"error": "Selected file is empty"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file format. Only CSV files are supported."}), 400

    try:
        df = pd.read_csv(file)
        total_records = len(df)
        missing_values = int(df.isnull().sum().sum())
        
        # Column requirements validation
        required_cols = {
            'water_quality': ['station_id', 'ph', 'dissolved_oxygen', 'turbidity'],
            'iot_sensors': ['station_id', 'ph', 'temperature', 'dissolved_oxygen', 'turbidity', 'tds'],
            'satellite': ['station_id', 'latitude', 'longitude', 'satellite_index', 'turbidity_proxy']
        }

        req = required_cols.get(dataset_type, ['station_id'])
        missing_cols = [c for c in req if c not in df.columns]

        if missing_cols:
            return jsonify({
                "error": f"Uploaded CSV missing required columns: {', '.join(missing_cols)}",
                "valid": False
            }), 400

        valid_records = total_records - int(df[req].isnull().any(axis=1).sum())
        invalid_records = total_records - valid_records

        # Save uploaded copy
        save_name = f"uploaded_{dataset_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(os.path.join(Config.UPLOAD_FOLDER, save_name), index=False)

        return jsonify({
            "message": "Dataset validated and uploaded successfully!",
            "valid": True,
            "filename": file.filename,
            "saved_as": save_name,
            "dataset_type": dataset_type,
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "missing_values": missing_values,
            "preview": df.head(5).to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV file: {str(e)}"}), 500
