"""
Water Quality Index (WQI) Calculation Service
Utilizes Weighted Arithmetic Water Quality Index Method.
Academic prototype implementation for Ganga River Water Quality DSS.
"""

def calculate_wqi(ph, do, turbidity, tds, bod, cod):
    """
    Calculate WQI, Quality Category, and Pollution Risk based on standard parameters.
    
    Parameters:
    - ph: pH level (unitless)
    - do: Dissolved Oxygen (mg/L)
    - turbidity: Turbidity (NTU)
    - tds: Total Dissolved Solids (mg/L)
    - bod: Biological Oxygen Demand (mg/L)
    - cod: Chemical Oxygen Demand (mg/L)
    
    Returns:
    - dict with keys: 'wqi', 'category', 'pollution_risk', 'sub_indices'
    """
    # Standard ideal and permissible values
    # pH ideal: 7.0, max permissible: 8.5
    # DO ideal: 14.6, standard min: 5.0
    # Turbidity standard: 5.0 NTU
    # TDS standard: 500.0 mg/L
    # BOD standard: 3.0 mg/L
    # COD standard: 10.0 mg/L
    
    # Sub-indices (q_i)
    q_ph = (abs(ph - 7.0) / 1.5) * 100.0
    
    # For DO, higher is better, so relative index measures deficit from ideal saturated DO (14.6)
    do_clamped = max(0.0, min(14.6, do))
    q_do = (abs(14.6 - do_clamped) / (14.6 - 5.0)) * 100.0
    
    q_turbidity = (turbidity / 5.0) * 100.0
    q_tds = (tds / 500.0) * 100.0
    q_bod = (bod / 3.0) * 100.0
    q_cod = (cod / 10.0) * 100.0

    # Parameter Weights (Sum = 1.0)
    w_ph = 0.20
    w_do = 0.26
    w_turbidity = 0.16
    w_tds = 0.08
    w_bod = 0.18
    w_cod = 0.12

    # Overall WQI
    wqi_score = (
        (q_ph * w_ph) +
        (q_do * w_do) +
        (q_turbidity * w_turbidity) +
        (q_tds * w_tds) +
        (q_bod * w_bod) +
        (q_cod * w_cod)
    )

    wqi_score = round(max(0.0, wqi_score), 2)

    # Categorization based on WQI score
    if wqi_score <= 25.0:
        category = "Excellent"
        pollution_risk = "Low"
    elif wqi_score <= 50.0:
        category = "Good"
        pollution_risk = "Low"
    elif wqi_score <= 75.0:
        category = "Moderate"
        pollution_risk = "Moderate"
    elif wqi_score <= 100.0:
        category = "Poor"
        pollution_risk = "High"
    else:
        category = "Critical"
        pollution_risk = "Severe"

    return {
        "wqi": wqi_score,
        "category": category,
        "pollution_risk": pollution_risk,
        "sub_indices": {
            "q_ph": round(q_ph, 2),
            "q_do": round(q_do, 2),
            "q_turbidity": round(q_turbidity, 2),
            "q_tds": round(q_tds, 2),
            "q_bod": round(q_bod, 2),
            "q_cod": round(q_cod, 2)
        }
    }
