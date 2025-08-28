# ml-service/src/services/anomaly_service.py

import os
import pandas as pd
import numpy as np
from datetime import datetime

# Import components from other modules within ml-service
from src.models import model_loader
from src.models.anomaly_detector import IsolationForestAnomalyDetector # Assuming this is your wrapper
from src.services.data_preprocessing import preprocess_data, MONITORED_FEATURES
from src.utils import model_utils # For saving models
from src.config.ml_config import MLConfig # For model paths and thresholds

# Load model and scaler globally when service starts
# This makes subsequent predictions faster as models are in memory
try:
    _current_anomaly_model = model_loader.load_model(MLConfig.ANOMALY_MODEL_PATH)
    _current_scaler = model_loader.load_scaler(MLConfig.SCALER_PATH)
except FileNotFoundError as e:
    print(f"Warning: {e}. Anomaly detection model or scaler not found. "
          "Please train the model first before attempting detection.")
    _current_anomaly_model = None
    _current_scaler = None
except Exception as e:
    print(f"Error loading anomaly model or scaler: {e}")
    _current_anomaly_model = None
    _current_scaler = None


def detect_anomaly_data(sensor_id: str, timestamp: str, data: dict) -> dict:
    """
    Detects anomalies in a single point of sensor data using the loaded model.

    Args:
        sensor_id (str): ID of the sensor.
        timestamp (str): Timestamp of the data.
        data (dict): Dictionary of sensor readings (e.g., {"temperature": 25.0, "humidity": 60.0}).

    Returns:
        dict: A dictionary containing 'is_anomaly' (bool), 'anomaly_score' (float),
              and 'monitored_features' (list of str).
    
    Raises:
        ValueError: If model or scaler is not loaded.
    """
    global _current_anomaly_model, _current_scaler

    if _current_anomaly_model is None or _current_scaler is None:
        raise ValueError("Anomaly detection model or scaler not loaded. "
                         "Please ensure the model is trained and available.")

    # 1. Preprocess the incoming data
    try:
        processed_data = preprocess_data(data, scaler=_current_scaler)
    except Exception as e:
        raise ValueError(f"Data preprocessing failed: {e}")

    # 2. Predict using the anomaly model
    # Isolation Forest's decision_function gives anomaly scores
    # Lower score usually means more anomalous.
    anomaly_score = _current_anomaly_model.decision_function(processed_data)[0]
    
    # Isolation Forest's predict method gives -1 for outliers, 1 for inliers
    prediction = _current_anomaly_model.predict(processed_data)[0]
    
    # Determine if it's an anomaly based on the model's prediction or a threshold
    # Using the prediction from model.predict() is often more straightforward for -1/1
    is_anomaly = True if prediction == -1 else False
    
    # You could also use a threshold on the anomaly_score:
    # is_anomaly = anomaly_score < MLConfig.ANOMALY_THRESHOLD # Define this in ml_config.py if using scores

    return {
        "sensor_id": sensor_id,
        "timestamp": timestamp,
        "is_anomaly": is_anomaly,
        "anomaly_score": float(anomaly_score), # Ensure it's a serializable float
        "monitored_features": MONITORED_FEATURES
    }

def train_anomaly_model(historical_data: list[dict]) -> dict:
    """
    Trains a new Isolation Forest model using historical data and saves it.
    
    Args:
        historical_data (list[dict]): List of historical sensor data points.
                                      Each dict should contain the MONITORED_FEATURES.
                                      Example: [{"temperature": 20.0, "humidity": 50.0}, ...]
    
    Returns:
        dict: Status of the training process.
        
    Raises:
        ValueError: If no historical data is provided or training fails.
    """
    global _current_anomaly_model, _current_scaler

    if not historical_data:
        raise ValueError("No historical data provided for training.")

    print(f"Starting anomaly model training with {len(historical_data)} data points...")

    try:
        # 1. Preprocess data and train a new scaler
        # We pass train_scaler=True to preprocess_data to get a new scaler
        processed_data_array, new_scaler = preprocess_data(historical_data, train_scaler=True)
        
        # 2. Initialize and train the anomaly detector
        # Pass parameters from MLConfig if needed (e.g., n_estimators, contamination)
        new_anomaly_detector = IsolationForestAnomalyDetector(
            n_estimators=MLConfig.IF_N_ESTIMATORS,
            contamination=MLConfig.IF_CONTAMINATION,
            random_state=MLConfig.RANDOM_SEED # For reproducibility
        )
        new_anomaly_detector.train(processed_data_array)
        
        # 3. Save the trained model and scaler
        model_utils.save_model(new_anomaly_detector.model, MLConfig.ANOMALY_MODEL_PATH)
        model_utils.save_scaler(new_scaler, MLConfig.SCALER_PATH)

        # Update the globally loaded models/scalers
        _current_anomaly_model = new_anomaly_detector.model
        _current_scaler = new_scaler
        
        print("Anomaly model training completed and saved.")
        return {"status": "training_completed", "message": "Anomaly model trained and saved successfully."}

    except Exception as e:
        print(f"Error during anomaly model training: {e}")
        raise Exception(f"Anomaly model training failed: {e}")

# --- Example of how other services might interact ---
# You'd have similar functions for forecasting and clustering services

# def predict_sensor_forecast(sensor_id: str, historical_readings: list[float], steps: int) -> dict:
#     """
#     Provides a forecast for a given sensor based on historical data.
#     This would use sensor_forecasting.py or lstm_forecasting.py
#     """
#     # Example implementation structure:
#     # Load relevant forecasting model (if specific to sensor or type)
#     # Preprocess historical_readings
#     # Call forecasting logic from src.services.sensor_forecasting
#     # Return predictions
#     pass

# def cluster_sensor_behavior(historical_behaviors: list[dict]) -> dict:
#     """
#     Clusters sensors based on their historical behavior patterns.
#     This would use clustering_service.py
#     """
#     # Example implementation structure:
#     # Preprocess historical_behaviors (e.g., feature engineering)
#     # Call clustering logic from src.services.clustering_service
#     # Return cluster assignments or insights
#     pass