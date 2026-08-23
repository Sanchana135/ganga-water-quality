"""
Machine Learning Pipeline & Model Training Script
Trains RandomForest Regressor & Classifier models on water quality dataset,
evaluates performance metrics (MAE, RMSE, R2, Accuracy, F1),
and saves model artifact using Joblib.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from config import Config

def train_and_evaluate():
    csv_path = os.path.join(Config.UPLOAD_FOLDER, 'demo_water_quality.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run seed_data.py first.")

    print(f"Loading water quality dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Feature Engineering
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Add realistic environmental dynamics (e.g. synthetic rainfall variable)
    np.random.seed(42)
    df['rainfall_mm'] = np.random.exponential(scale=12.0, size=len(df))

    feature_cols = [
        'station_id', 'ph', 'temperature', 'dissolved_oxygen', 
        'turbidity', 'tds', 'conductivity', 'bod', 'cod', 
        'rainfall_mm', 'hour', 'month'
    ]

    X = df[feature_cols]
    y_wqi = df['wqi']
    y_do = df['dissolved_oxygen']
    y_turb = df['turbidity']
    y_cat = df['quality_category']

    # Train / Test Split (80% Train, 20% Test)
    X_train, X_test, y_train_wqi, y_test_wqi = train_test_split(X, y_wqi, test_size=0.2, random_state=42)
    _, _, y_train_cat, y_test_cat = train_test_split(X, y_cat, test_size=0.2, random_state=42)
    _, _, y_train_do, y_test_do = train_test_split(X, y_do, test_size=0.2, random_state=42)
    _, _, y_train_turb, y_test_turb = train_test_split(X, y_turb, test_size=0.2, random_state=42)

    print(f"Training set size: {len(X_train)} samples, Test set size: {len(X_test)} samples.")

    # 1. Train Regressor for WQI
    print("Training RandomForestRegressor for WQI...")
    reg_wqi = RandomForestRegressor(n_estimators=100, random_state=42)
    reg_wqi.fit(X_train, y_train_wqi)

    # 2. Train Regressor for DO
    reg_do = RandomForestRegressor(n_estimators=100, random_state=42)
    reg_do.fit(X_train, y_train_do)

    # 3. Train Regressor for Turbidity
    reg_turb = RandomForestRegressor(n_estimators=100, random_state=42)
    reg_turb.fit(X_train, y_train_turb)

    # 4. Train Classifier for Quality Category
    print("Training RandomForestClassifier for WQI Category...")
    clf_cat = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_cat.fit(X_train, y_train_cat)

    # Predictions & Evaluation
    preds_wqi = reg_wqi.predict(X_test)
    mae = mean_absolute_error(y_test_wqi, preds_wqi)
    rmse = np.sqrt(mean_squared_error(y_test_wqi, preds_wqi))
    r2 = r2_score(y_test_wqi, preds_wqi)

    preds_cat = clf_cat.predict(X_test)
    accuracy = accuracy_score(y_test_cat, preds_cat)
    precision = precision_score(y_test_cat, preds_cat, average='weighted', zero_division=0)
    recall = recall_score(y_test_cat, preds_cat, average='weighted', zero_division=0)
    f1 = f1_score(y_test_cat, preds_cat, average='weighted', zero_division=0)

    print("\n" + "="*50)
    print("       MODEL EVALUATION METRICS (TEST SET)      ")
    print("="*50)
    print(f"Regression (WQI Prediction):")
    print(f"  - Mean Absolute Error (MAE):  {mae:.4f}")
    print(f"  - Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"  - R² Score:                   {r2:.4f}")
    print(f"\nClassification (Quality Category):")
    print(f"  - Accuracy:                   {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  - Precision (Weighted):       {precision:.4f}")
    print(f"  - Recall (Weighted):          {recall:.4f}")
    print(f"  - F1-Score (Weighted):        {f1:.4f}")
    print("="*50 + "\n")

    # Save artifacts
    model_pipeline = {
        "reg_wqi": reg_wqi,
        "reg_do": reg_do,
        "reg_turb": reg_turb,
        "clf_cat": clf_cat,
        "feature_cols": feature_cols
    }
    
    os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
    joblib.dump(model_pipeline, Config.MODEL_PATH)
    print(f"Trained model pipeline saved successfully to {Config.MODEL_PATH}")

    # Save metrics JSON for frontend UI display
    metrics_data = {
        "model_type": "RandomForest Ensembles (Regressor & Classifier)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "features_used": feature_cols
    }
    
    metrics_path = os.path.join(Config.BASE_DIR, 'models', 'model_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=4)
    print(f"Metrics saved to {metrics_path}")

if __name__ == '__main__':
    train_and_evaluate()
