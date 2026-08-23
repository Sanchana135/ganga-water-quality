"""
AI Decision Support System (DSS) Recommendation Engine
Synthesizes IoT measurements, satellite remote sensing, dynamic trends, and ML forecasts
to formulate actionable environmental management advice.
"""

def generate_dss_recommendations(station_name, current_reading, wqi_info, forecast_info=None, satellite_info=None):
    """
    Generates dynamic advisory recommendations based on environmental parameters.
    
    Parameters:
    - station_name: Name of monitoring station
    - current_reading: Dict or SensorReading object containing current parameters
    - wqi_info: Dict containing WQI score, category, pollution risk
    - forecast_info: Optional dict with predicted parameters
    - satellite_info: Optional dict with satellite proxies
    
    Returns:
    - Dict with executive summary, risk level, primary factors, and categorized recommendations.
    """
    ph = getattr(current_reading, 'ph', current_reading.get('ph', 7.2))
    do = getattr(current_reading, 'dissolved_oxygen', current_reading.get('dissolved_oxygen', 6.5))
    turb = getattr(current_reading, 'turbidity', current_reading.get('turbidity', 12.0))
    tds = getattr(current_reading, 'tds', current_reading.get('tds', 250.0))
    bod = getattr(current_reading, 'bod', current_reading.get('bod', 2.5))
    cod = getattr(current_reading, 'cod', current_reading.get('cod', 8.0))

    wqi = wqi_info.get('wqi', 45.0)
    category = wqi_info.get('category', 'Good')
    pollution_risk = wqi_info.get('pollution_risk', 'Low')

    recommendations = []
    immediate_actions = []
    long_term_strategies = []
    key_drivers = []

    # 1. Dissolved Oxygen Analysis
    if do < 4.0:
        key_drivers.append("Severe DO Depletion (Organic Loading)")
        immediate_actions.append(
            f"Deploy mobile aeration units near {station_name} intake zones and inspect upstream industrial effluent discharge."
        )
        recommendations.append(
            "Increase hourly sampling frequency for BOD and COD to locate organic pollutant sources upstream."
        )
    elif do < 5.5:
        key_drivers.append("Moderate DO Deficit")
        recommendations.append(
            "Monitor aquatic dissolved oxygen continuously. Check for thermal discharge or agricultural nutrient runoff."
        )

    # 2. Turbidity & Suspended Solids Analysis
    if turb > 45.0:
        key_drivers.append("High Sedimentation & Soil Erosion")
        immediate_actions.append(
            f"Alert downstream water treatment facilities near {station_name} to adjust coagulant dosing for high turbidity."
        )
        recommendations.append(
            "Investigate upstream riverbank construction, sand mining activities, or heavy rainfall runoff using satellite imagery."
        )

    # 3. Organic Pollution Analysis (BOD / COD)
    if bod > 6.0 or cod > 20.0:
        key_drivers.append("Industrial / Untreated Sewage Discharge")
        immediate_actions.append(
            f"Dispatch environmental inspection team to audit municipal sewage treatment plants (STPs) operating near {station_name}."
        )
        long_term_strategies.append(
            "Enforce strict Zero Liquid Discharge (ZLD) protocols on industrial clusters along the river segment."
        )

    # 4. pH Deviation Analysis
    if ph < 6.5 or ph > 8.5:
        key_drivers.append(f"Chemical Anomaly (pH: {ph:.1f})")
        immediate_actions.append(
            f"Verify calibration of sensor probes at {station_name} station and take chemical grab samples for laboratory verification."
        )

    # 5. Forecast & Trend Integration
    if forecast_info:
        pred_wqi = forecast_info.get('predicted_wqi', wqi)
        if pred_wqi > wqi + 10.0:
            recommendations.append(
                f"AI Model forecasts a degradation in water quality over the next {forecast_info.get('horizon_hours', 24)}h. Issue preliminary warning to local river authorities."
            )
        elif pred_wqi < wqi - 5.0:
            recommendations.append(
                "AI Model forecasts improving water quality conditions over the coming forecast window."
            )

    # General baseline advice if water is good
    if not immediate_actions:
        immediate_actions.append("Maintain standard automated monitoring protocols and regular telemetry verification.")

    if not long_term_strategies:
        long_term_strategies.append("Continue seasonal Ganga River Basin environmental flow (E-Flow) assessments.")

    executive_summary = (
        f"Station {station_name} currently displays a Water Quality Index of {wqi:.1f} ({category} condition). "
        f"Pollution risk level is evaluated as {pollution_risk.upper()}."
    )

    return {
        "station_name": station_name,
        "wqi": wqi,
        "category": category,
        "pollution_risk": pollution_risk,
        "executive_summary": executive_summary,
        "key_drivers": key_drivers if key_drivers else ["Baseline Natural River Flow"],
        "immediate_actions": immediate_actions,
        "recommendations": recommendations,
        "long_term_strategies": long_term_strategies,
        "disclaimer": "Advisories generated by AI Decision Support System algorithm for environmental planning and operational decision support."
    }
