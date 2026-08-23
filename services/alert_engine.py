"""
Alert & Early Warning Engine
Monitors water quality parameters and triggers automated early warning notifications.
"""

from database import db, Alert

def evaluate_reading_alerts(station_id, station_name, reading, wqi_result):
    """
    Evaluates a new sensor reading against ecological safety thresholds.
    Creates and saves Alert records in DB if thresholds are exceeded.
    """
    alerts_triggered = []
    
    # 1. Dissolved Oxygen Threshold Check
    do = reading.dissolved_oxygen
    if do < 3.0:
        alerts_triggered.append({
            "alert_type": "Critical Low Dissolved Oxygen",
            "parameter": "Dissolved Oxygen (DO)",
            "current_value": do,
            "threshold": 3.0,
            "severity": "CRITICAL",
            "message": f"Severe oxygen depletion at {station_name} (DO: {do:.2f} mg/L). High threat to aquatic life."
        })
    elif do < 4.5:
        alerts_triggered.append({
            "alert_type": "Low Dissolved Oxygen Warning",
            "parameter": "Dissolved Oxygen (DO)",
            "current_value": do,
            "threshold": 4.5,
            "severity": "HIGH",
            "message": f"Dissolved Oxygen at {station_name} dropped to {do:.2f} mg/L (Below desirable 5.0 mg/L)."
        })

    # 2. Water Quality Index (WQI) Threshold Check
    wqi = wqi_result['wqi']
    if wqi > 100.0:
        alerts_triggered.append({
            "alert_type": "Critical Water Quality Pollution",
            "parameter": "Water Quality Index (WQI)",
            "current_value": wqi,
            "threshold": 100.0,
            "severity": "CRITICAL",
            "message": f"Critical pollution alert at {station_name}! WQI score reached {wqi:.2f} (Status: Critical)."
        })
    elif wqi > 75.0:
        alerts_triggered.append({
            "alert_type": "High Pollution Level",
            "parameter": "Water Quality Index (WQI)",
            "current_value": wqi,
            "threshold": 75.0,
            "severity": "HIGH",
            "message": f"Water quality at {station_name} degraded to Poor condition (WQI: {wqi:.2f})."
        })

    # 3. Turbidity Threshold Check
    turb = reading.turbidity
    if turb > 65.0:
        alerts_triggered.append({
            "alert_type": "Severe Turbidity & Sedimentation",
            "parameter": "Turbidity",
            "current_value": turb,
            "threshold": 65.0,
            "severity": "HIGH",
            "message": f"High sediment runoff detected at {station_name} (Turbidity: {turb:.2f} NTU)."
        })
    elif turb > 35.0:
        alerts_triggered.append({
            "alert_type": "Elevated Turbidity Warning",
            "parameter": "Turbidity",
            "current_value": turb,
            "threshold": 35.0,
            "severity": "WARNING",
            "message": f"Turbidity elevated at {station_name} ({turb:.2f} NTU)."
        })

    # 4. pH Threshold Check
    ph = reading.ph
    if ph < 6.5 or ph > 8.5:
        severity = "HIGH" if (ph < 6.0 or ph > 9.0) else "WARNING"
        alerts_triggered.append({
            "alert_type": "pH Anomaly Detected",
            "parameter": "pH",
            "current_value": ph,
            "threshold": 8.5 if ph > 8.5 else 6.5,
            "severity": severity,
            "message": f"pH anomaly recorded at {station_name} (pH: {ph:.2f}). Outside neutral ecological range 6.5 - 8.5."
        })

    # Save created alerts to database
    db_alerts = []
    for item in alerts_triggered:
        # Avoid creating duplicate active alerts for the exact same parameter within short timeframe
        existing = Alert.query.filter_by(
            station_id=station_id, 
            parameter=item['parameter'], 
            resolved=False
        ).first()
        
        if not existing:
            alert_obj = Alert(
                station_id=station_id,
                alert_type=item['alert_type'],
                parameter=item['parameter'],
                current_value=item['current_value'],
                threshold=item['threshold'],
                message=item['message'],
                severity=item['severity'],
                resolved=False
            )
            db.session.add(alert_obj)
            db_alerts.append(alert_obj)
            
    if db_alerts:
        db.session.commit()
        
    return [a.to_dict() for a in db_alerts]
