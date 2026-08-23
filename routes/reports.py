"""
Reports Generation Blueprint
Generates comprehensive Ganga River Basin Water Quality Assessment Reports.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, render_template, request
from database import db, Station, SensorReading, WaterQuality, Alert
from routes.auth import login_required
from services.recommendation_engine import generate_dss_recommendations
from services.forecast_engine import forecast_engine

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/reports/generate', methods=['POST'])
@login_required
def generate_report_data():
    data = request.get_json() or {}
    station_id = int(data.get('station_id', 3))
    days = int(data.get('days', 30))

    st = Station.query.get_or_404(station_id)
    cutoff = datetime.utcnow() - timedelta(days=days)

    readings = SensorReading.query.filter_by(station_id=station_id).filter(SensorReading.timestamp >= cutoff).all()
    wqi_logs = WaterQuality.query.filter_by(station_id=station_id).filter(WaterQuality.timestamp >= cutoff).all()

    wqi_scores = [w.wqi for w in wqi_logs] if wqi_logs else [50.0]
    do_values = [r.dissolved_oxygen for r in readings] if readings else [6.5]
    turb_values = [r.turbidity for r in readings] if readings else [15.0]

    avg_wqi = round(sum(wqi_scores) / len(wqi_scores), 2)
    min_wqi = round(min(wqi_scores), 2)
    max_wqi = round(max(wqi_scores), 2)

    avg_do = round(sum(do_values) / len(do_values), 2)
    avg_turb = round(sum(turb_values) / len(turb_values), 2)

    last_r = readings[-1] if readings else None
    last_wq = wqi_logs[-1] if wqi_logs else None

    # Run 24h AI forecast for report
    current_params = last_r.to_dict() if last_r else {}
    fc_res = forecast_engine.predict_horizon(station_id, current_params, 24, 0.0)

    # DSS advisories
    dss_advice = generate_dss_recommendations(
        st.name, 
        last_r.to_dict() if last_r else {}, 
        last_wq.to_dict() if last_wq else {"wqi": avg_wqi, "category": "Moderate", "pollution_risk": "Moderate"}
    )

    alerts = Alert.query.filter_by(station_id=station_id).filter(Alert.created_at >= cutoff).all()

    report_payload = {
        "generated_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "station": st.to_dict(),
        "period_days": days,
        "total_observations": len(readings),
        "summary": {
            "avg_wqi": avg_wqi,
            "min_wqi": min_wqi,
            "max_wqi": max_wqi,
            "avg_do": avg_do,
            "avg_turbidity": avg_turb,
            "quality_category": last_wq.quality_category if last_wq else "Moderate",
            "pollution_risk": last_wq.pollution_risk if last_wq else "Moderate"
        },
        "forecast_24h": fc_res,
        "alerts_count": len(alerts),
        "alerts": [a.to_dict() for a in alerts[:5]],
        "dss_recommendations": dss_advice
    }

    return jsonify(report_payload)

@reports_bp.route('/reports/print')
@login_required
def print_report_view():
    station_id = int(request.args.get('station_id', 3))
    days = int(request.args.get('days', 30))

    st = Station.query.get_or_404(station_id)
    cutoff = datetime.utcnow() - timedelta(days=days)

    readings = SensorReading.query.filter_by(station_id=station_id).filter(SensorReading.timestamp >= cutoff).all()
    wqi_logs = WaterQuality.query.filter_by(station_id=station_id).filter(WaterQuality.timestamp >= cutoff).all()

    wqi_scores = [w.wqi for w in wqi_logs] if wqi_logs else [50.0]
    do_values = [r.dissolved_oxygen for r in readings] if readings else [6.5]
    turb_values = [r.turbidity for r in readings] if readings else [15.0]

    avg_wqi = round(sum(wqi_scores) / len(wqi_scores), 2)
    min_wqi = round(min(wqi_scores), 2)
    max_wqi = round(max(wqi_scores), 2)
    avg_do = round(sum(do_values) / len(do_values), 2)
    avg_turb = round(sum(turb_values) / len(turb_values), 2)

    last_r = readings[-1] if readings else None
    last_wq = wqi_logs[-1] if wqi_logs else None

    fc_res = forecast_engine.predict_horizon(station_id, last_r.to_dict() if last_r else {}, 24, 0.0)
    dss_advice = generate_dss_recommendations(st.name, last_r.to_dict() if last_r else {}, last_wq.to_dict() if last_wq else {"wqi": avg_wqi, "category": "Moderate", "pollution_risk": "Moderate"})
    alerts = Alert.query.filter_by(station_id=station_id).filter(Alert.created_at >= cutoff).all()

    return render_template(
        'report_template.html',
        generated_at=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        station=st,
        period_days=days,
        readings_count=len(readings),
        avg_wqi=avg_wqi,
        min_wqi=min_wqi,
        max_wqi=max_wqi,
        avg_do=avg_do,
        avg_turb=avg_turb,
        last_wq=last_wq,
        last_r=last_r,
        forecast=fc_res,
        dss=dss_advice,
        alerts=alerts
    )
