"""
AI Forecast Engine Service
Loads trained Joblib Random Forest models and executes dynamic multi-horizon predictions
for water quality index, dissolved oxygen, turbidity, and quality category.
"""

import os
import json
import joblib
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from config import Config
from services.water_quality import calculate_wqi

class ForecastEngine:
    def __init__(self):
        self.model_pipeline = None
        self.metrics = None
        self.load_models()

    def load_models(self):
        """Loads trained Joblib ML artifact and metrics JSON."""
        if os.path.exists(Config.MODEL_PATH):
            try:
                self.model_pipeline = joblib.load(Config.MODEL_PATH)
            except Exception as e:
                print(f"Error loading ML model: {e}")
                self.model_pipeline = None

        metrics_path = os.path.join(Config.BASE_DIR, 'models', 'model_metrics.json')
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
            except Exception:
                self.metrics = None

    def predict_horizon(self, station_id, current_params, horizon_hours=24, expected_rainfall_mm=0.0):
        """
        Executes dynamic forecast prediction for a specified station and horizon.
        
        Parameters:
        - station_id: int
        - current_params: dict (ph, temperature, dissolved_oxygen, turbidity, tds, conductivity, bod, cod)
        - horizon_hours: int (6, 12, 24, 72)
        - expected_rainfall_mm: float
        """
        now = datetime.utcnow()
        target_time = now + timedelta(hours=horizon_hours)

        ph = float(current_params.get('ph', 7.2))
        temp = float(current_params.get('temperature', 22.0))
        do = float(current_params.get('dissolved_oxygen', 6.5))
        turb = float(current_params.get('turbidity', 12.0))
        tds = float(current_params.get('tds', 250.0))
        cond = float(current_params.get('conductivity', tds * 1.56))
        bod = float(current_params.get('bod', 2.5))
        cod = float(current_params.get('cod', 8.0))

        # Dynamic parameter drift over horizon based on rainfall & organic load
        # Rainfall increases turbidity & TDS, slightly reduces DO
        turb_drift = turb + (expected_rainfall_mm * 1.8) + (horizon_hours * 0.08)
        do_drift = max(0.5, do - (expected_rainfall_mm * 0.05) - (bod * 0.04 * (horizon_hours / 24.0)))
        bod_drift = bod + (expected_rainfall_mm * 0.12)
        cod_drift = cod + (expected_rainfall_mm * 0.35)
        ph_drift = ph + (np.sin(target_time.hour / 24.0 * 2 * np.pi) * 0.15)

        input_df = pd.DataFrame([{
            'station_id': int(station_id),
            'ph': ph_drift,
            'temperature': temp + (1.5 if 12 <= target_time.hour <= 16 else -1.0),
            'dissolved_oxygen': do_drift,
            'turbidity': turb_drift,
            'tds': tds + (expected_rainfall_mm * 2.5),
            'conductivity': cond + (expected_rainfall_mm * 3.8),
            'bod': bod_drift,
            'cod': cod_drift,
            'rainfall_mm': expected_rainfall_mm,
            'hour': target_time.hour,
            'month': target_time.month
        }])

        if self.model_pipeline:
            try:
                reg_wqi = self.model_pipeline['reg_wqi']
                reg_do = self.model_pipeline['reg_do']
                reg_turb = self.model_pipeline['reg_turb']
                clf_cat = self.model_pipeline['clf_cat']

                pred_wqi = float(reg_wqi.predict(input_df)[0])
                pred_do = float(reg_do.predict(input_df)[0])
                pred_turb = float(reg_turb.predict(input_df)[0])
                pred_cat = str(clf_cat.predict(input_df)[0])
            except Exception as e:
                print(f"Prediction inference error: {e}")
                # Fallback to WQI engine calculation
                wqi_calc = calculate_wqi(ph_drift, do_drift, turb_drift, tds, bod_drift, cod_drift)
                pred_wqi = wqi_calc['wqi']
                pred_do = do_drift
                pred_turb = turb_drift
                pred_cat = wqi_calc['category']
        else:
            wqi_calc = calculate_wqi(ph_drift, do_drift, turb_drift, tds, bod_drift, cod_drift)
            pred_wqi = wqi_calc['wqi']
            pred_do = do_drift
            pred_turb = turb_drift
            pred_cat = wqi_calc['category']

        # Confidence decay with horizon length
        confidence = max(75.0, 96.5 - (horizon_hours * 0.22))

        return {
            "station_id": station_id,
            "forecast_time": target_time.strftime('%Y-%m-%d %H:%M:%S'),
            "horizon_hours": horizon_hours,
            "expected_rainfall_mm": expected_rainfall_mm,
            "predicted_wqi": round(max(0.0, pred_wqi), 2),
            "predicted_category": pred_cat,
            "predicted_do": round(max(0.0, pred_do), 2),
            "predicted_turbidity": round(max(0.0, pred_turb), 2),
            "confidence": round(confidence, 1)
        }

# Global singleton instance
forecast_engine = ForecastEngine()
