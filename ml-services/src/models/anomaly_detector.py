# ml-service/src/models/anomaly_detector.py

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Constants
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models/isolation_forest.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '../../models/scaler.pkl')


class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.scaler = None

        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.load_model()
        else:
            self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            self.scaler = StandardScaler()

    def train(self, df: pd.DataFrame, features: list):
        """
        Train the Isolation Forest model on selected features and save model and scaler.
        """
        print("[INFO] Training anomaly detection model...")
        df_clean = df[features].copy().dropna()

        # Fit scaler and transform data
        self.scaler.fit(df_clean)
        X_scaled = self.scaler.transform(df_clean)

        # Train Isolation Forest
        self.model.fit(X_scaled)
        self.save_model()
        print("[INFO] Model training complete and saved.")

    def predict(self, df: pd.DataFrame, features: list):
        """
        Predict anomalies on input DataFrame using trained model.
        Returns DataFrame with anomaly flags and scores.
        """
        if self.model is None or self.scaler is None:
            raise Exception("Model or scaler not initialized. Train or load the model first.")

        df_copy = df.copy()
        df_features = df_copy[features].fillna(method='ffill').fillna(method='bfill')

        # Scale the data
        X_scaled = self.scaler.transform(df_features)

        # Predict anomaly (-1 = anomaly, 1 = normal)
        preds = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        df_copy['anomaly'] = preds
        df_copy['anomaly_score'] = scores

        return df_copy

    def save_model(self):
        """
        Save the trained model and scaler.
        """
        joblib.dump(self.model, MODEL_PATH)
        joblib.dump(self.scaler, SCALER_PATH)
        print(f"[INFO] Model saved at {MODEL_PATH}")
        print(f"[INFO] Scaler saved at {SCALER_PATH}")

    def load_model(self):
        """
        Load the trained model and scaler.
        """
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        print(f"[INFO] Model loaded from {MODEL_PATH}")
        print(f"[INFO] Scaler loaded from {SCALER_PATH}")
