# ml-service/tests/test_anomaly_service.py

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Import the service to be tested
from src.services import anomaly_service
from src.models.anomaly_detector import IsolationForestAnomalyDetector
from src.config.ml_config import MLConfig

# Define some dummy data for testing
DUMMY_SENSOR_DATA_POINT = {
    "temperature": 25.0,
    "humidity": 60.0,
    "pressure": 1012.0,
    "vibration": 1.5
}
DUMMY_HISTORICAL_DATA = [
    {"temperature": 20.0, "humidity": 50.0, "pressure": 1000.0, "vibration": 1.0},
    {"temperature": 21.0, "humidity": 51.0, "pressure": 1001.0, "vibration": 1.1},
    {"temperature": 22.0, "humidity": 52.0, "pressure": 1002.0, "vibration": 1.2},
    {"temperature": 200.0, "humidity": 10.0, "pressure": 500.0, "vibration": 50.0} # An outlier for training
]

# Fixture to reset the anomaly_service's global model/scaler before each test
# This prevents tests from affecting each other's state
@pytest.fixture(autouse=True)
def reset_anomaly_service_globals():
    original_model = anomaly_service._current_anomaly_model
    original_scaler = anomaly_service._current_scaler
    
    anomaly_service._current_anomaly_model = None
    anomaly_service._current_scaler = None
    yield
    anomaly_service._current_anomaly_model = original_model
    anomaly_service._current_scaler = original_scaler

# --- Tests for detect_anomaly_data ---
@patch('src.models.model_loader.load_model')
@patch('src.models.model_loader.load_scaler')
@patch('src.services.data_preprocessing.preprocess_data')
def test_detect_anomaly_data_success(mock_preprocess_data, mock_load_scaler, mock_load_model, reset_anomaly_service_globals):
    # Mock loaded model and scaler behavior
    mock_model = MagicMock()
    mock_scaler = MagicMock()

    # Configure the mock model's decision_function and predict method
    mock_model.decision_function.return_value = np.array([-0.5]) # A score indicating non-anomaly
    mock_model.predict.return_value = np.array([1]) # 1 for inlier, -1 for outlier

    # Configure mock load functions to return our mock objects
    mock_load_model.return_value = mock_model
    mock_load_scaler.return_value = mock_scaler

    # Simulate that the model and scaler are loaded globally
    anomaly_service._current_anomaly_model = mock_model
    anomaly_service._current_scaler = mock_scaler

    # Mock preprocess_data to return a dummy processed array
    mock_processed_data = np.array([[0.1, 0.2, 0.3, 0.4]])
    mock_preprocess_data.return_value = mock_processed_data

    # Call the function under test
    result = anomaly_service.detect_anomaly_data("sensor123", "2023-01-01T12:00:00Z", DUMMY_SENSOR_DATA_POINT)

    # Assertions
    mock_preprocess_data.assert_called_once_with(DUMMY_SENSOR_DATA_POINT, scaler=mock_scaler)
    mock_model.decision_function.assert_called_once_with(mock_processed_data)
    mock_model.predict.assert_called_once_with(mock_processed_data)

    assert result["is_anomaly"] is False
    assert result["anomaly_score"] == -0.5
    assert result["sensor_id"] == "sensor123"
    assert result["timestamp"] == "2023-01-01T12:00:00Z"
    assert "monitored_features" in result # Check that features list is included


@patch('src.models.model_loader.load_model')
@patch('src.models.model_loader.load_scaler')
@patch('src.services.data_preprocessing.preprocess_data')
def test_detect_anomaly_data_anomaly_detected(mock_preprocess_data, mock_load_scaler, mock_load_model, reset_anomaly_service_globals):
    mock_model = MagicMock()
    mock_scaler = MagicMock()

    # Configure for anomaly detection
    mock_model.decision_function.return_value = np.array([-1.5]) # A score indicating anomaly
    mock_model.predict.return_value = np.array([-1]) # -1 for outlier

    mock_load_model.return_value = mock_model
    mock_load_scaler.return_value = mock_scaler

    anomaly_service._current_anomaly_model = mock_model
    anomaly_service._current_scaler = mock_scaler
    
    mock_preprocess_data.return_value = np.array([[0.9, 0.8, 0.7, 0.6]])

    result = anomaly_service.detect_anomaly_data("sensor456", "2023-01-01T13:00:00Z", DUMMY_SENSOR_DATA_POINT)

    assert result["is_anomaly"] is True
    assert result["anomaly_score"] == -1.5


def test_detect_anomaly_data_no_model_loaded(reset_anomaly_service_globals):
    # Ensure model and scaler are None as per reset_anomaly_service_globals fixture
    assert anomaly_service._current_anomaly_model is None
    assert anomaly_service._current_scaler is None

    with pytest.raises(ValueError, match="Anomaly detection model or scaler not loaded"):
        anomaly_service.detect_anomaly_data("sensor123", "2023-01-01T12:00:00Z", DUMMY_SENSOR_DATA_POINT)

@patch('src.services.data_preprocessing.preprocess_data', side_effect=Exception("Preprocessing error"))
@patch('src.models.model_loader.load_model')
@patch('src.models.model_loader.load_scaler')
def test_detect_anomaly_data_preprocessing_failure(mock_load_scaler, mock_load_model, mock_preprocess_data, reset_anomaly_service_globals):
    # Simulate model and scaler are loaded
    anomaly_service._current_anomaly_model = MagicMock()
    anomaly_service._current_scaler = MagicMock()

    with pytest.raises(ValueError, match="Data preprocessing failed"):
        anomaly_service.detect_anomaly_data("sensor123", "2023-01-01T12:00:00Z", DUMMY_SENSOR_DATA_POINT)
    mock_preprocess_data.assert_called_once()


# --- Tests for train_anomaly_model ---
@patch('src.services.data_preprocessing.preprocess_data')
@patch('src.models.anomaly_detector.IsolationForestAnomalyDetector')
@patch('src.utils.model_utils.save_model')
@patch('src.utils.model_utils.save_scaler')
def test_train_anomaly_model_success(
    mock_save_scaler, mock_save_model, MockIsolationForestAnomalyDetector, mock_preprocess_data, reset_anomaly_service_globals
):
    # Mock preprocess_data to return processed data and a new scaler
    mock_scaler_instance = MagicMock()
    mock_processed_data = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    mock_preprocess_data.return_value = (mock_processed_data, mock_scaler_instance)

    # Mock the IsolationForestAnomalyDetector and its train method
    mock_detector_instance = MagicMock()
    MockIsolationForestAnomalyDetector.return_value = mock_detector_instance
    mock_detector_instance.model = MagicMock() # Simulate that the detector has a .model attribute

    # Call the function under test
    result = anomaly_service.train_anomaly_model(DUMMY_HISTORICAL_DATA)

    # Assertions
    mock_preprocess_data.assert_called_once_with(DUMMY_HISTORICAL_DATA, train_scaler=True)
    MockIsolationForestAnomalyDetector.assert_called_once_with(
        n_estimators=MLConfig.IF_N_ESTIMATORS,
        contamination=MLConfig.IF_CONTAMINATION,
        random_state=MLConfig.RANDOM_SEED
    )
    mock_detector_instance.train.assert_called_once_with(mock_processed_data)
    mock_save_model.assert_called_once_with(mock_detector_instance.model, MLConfig.ANOMALY_MODEL_PATH)
    mock_save_scaler.assert_called_once_with(mock_scaler_instance, MLConfig.SCALER_PATH)

    assert result == {"status": "training_completed", "message": "Anomaly model trained and saved successfully."}
    # Check that global models are updated
    assert anomaly_service._current_anomaly_model is mock_detector_instance.model
    assert anomaly_service._current_scaler is mock_scaler_instance

def test_train_anomaly_model_no_data():
    with pytest.raises(ValueError, match="No historical data provided for training."):
        anomaly_service.train_anomaly_model([])

@patch('src.services.data_preprocessing.preprocess_data', side_effect=Exception("Preprocessing failed during training"))
def test_train_anomaly_model_preprocessing_failure(mock_preprocess_data):
    with pytest.raises(Exception, match="Anomaly model training failed"):
        anomaly_service.train_anomaly_model(DUMMY_HISTORICAL_DATA)
    mock_preprocess_data.assert_called_once()

@patch('src.models.anomaly_detector.IsolationForestAnomalyDetector', side_effect=Exception("Model training failed"))
@patch('src.services.data_preprocessing.preprocess_data')
def test_train_anomaly_model_training_failure(mock_preprocess_data, MockIsolationForestAnomalyDetector):
    mock_preprocess_data.return_value = (np.array([[1,2,3,4]]), MagicMock())
    with pytest.raises(Exception, match="Anomaly model training failed"):
        anomaly_service.train_anomaly_model(DUMMY_HISTORICAL_DATA)
    MockIsolationForestAnomalyDetector.assert_called_once()

# Test initial load warning/error handling (when files don't exist)
@patch('src.models.model_loader.load_model', side_effect=FileNotFoundError)
@patch('src.models.model_loader.load_scaler', side_effect=FileNotFoundError)
def test_anomaly_service_initial_load_handles_file_not_found(mock_load_scaler, mock_load_model):
    # This test primarily verifies the __init__ behavior of the module.
    # It will implicitly re-import/initialize the anomaly_service when run by pytest.
    # We check if the global variables are set to None
    assert anomaly_service._current_anomaly_model is None
    assert anomaly_service._current_scaler is None
    mock_load_model.assert_called_once()
    mock_load_scaler.assert_called_once()

# Test initial load with other exceptions
@patch('src.models.model_loader.load_model', side_effect=EOFError("Corrupted file"))
@patch('src.models.model_loader.load_scaler', side_effect=EOFError("Corrupted file"))
def test_anomaly_service_initial_load_handles_other_errors(mock_load_scaler, mock_load_model):
    assert anomaly_service._current_anomaly_model is None
    assert anomaly_service._current_scaler is None
    mock_load_model.assert_called_once()
    mock_load_scaler.assert_called_once()