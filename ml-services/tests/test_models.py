# ml-service/tests/test_models.py

import pytest
import numpy as np
import pandas as pd
import os
import pickle
from unittest.mock import MagicMock, patch

from src.models.anomaly_detector import IsolationForestAnomalyDetector
from src.models import model_loader
from src.utils import model_utils
from src.services.data_preprocessing import MONITORED_FEATURES # To get feature names


# Dummy data for testing models
# Needs to be 2D array, like what sklearn models expect
DUMMY_2D_DATA = np.array([
    [20.0, 50.0, 1000.0, 1.0],
    [21.0, 51.0, 1001.0, 1.1],
    [22.0, 52.0, 1002.0, 1.2],
    [5.0, 5.0, 50.0, 0.1] # Potential outlier
])

# --- Tests for IsolationForestAnomalyDetector ---
def test_isolation_forest_detector_init():
    detector = IsolationForestAnomalyDetector(n_estimators=50, contamination=0.05, random_state=42)
    assert detector.model is not None
    assert detector.model.n_estimators == 50
    assert detector.model.contamination == 0.05
    assert detector.model.random_state == 42

def test_isolation_forest_detector_train():
    detector = IsolationForestAnomalyDetector()
    detector.train(DUMMY_2D_DATA)
    # After training, the model should be fitted
    assert hasattr(detector.model, 'offset_')

def test_isolation_forest_detector_train_invalid_data():
    detector = IsolationForestAnomalyDetector()
    with pytest.raises(ValueError, match="Training data must be a 2D numpy array."):
        detector.train(np.array([1, 2, 3])) # 1D array
    with pytest.raises(ValueError, match="Training data must be a 2D numpy array."):
        detector.train("not an array") # Not an array

def test_isolation_forest_detector_predict():
    detector = IsolationForestAnomalyDetector()
    detector.train(DUMMY_2D_DATA)
    predictions = detector.predict(DUMMY_2D_DATA)
    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (DUMMY_2D_DATA.shape[0],)
    assert np.all(np.isin(predictions, [-1, 1])) # Isolation Forest predicts -1 for outliers, 1 for inliers

def test_isolation_forest_detector_predict_invalid_data():
    detector = IsolationForestAnomalyDetector()
    detector.train(DUMMY_2D_DATA) # Model must be trained first
    with pytest.raises(ValueError, match="Prediction data must be a 2D numpy array."):
        detector.predict(np.array([1, 2, 3])) # 1D array

def test_isolation_forest_detector_decision_function():
    detector = IsolationForestAnomalyDetector()
    detector.train(DUMMY_2D_DATA)
    scores = detector.decision_function(DUMMY_2D_DATA)
    assert isinstance(scores, np.ndarray)
    assert scores.shape == (DUMMY_2D_DATA.shape[0],)
    # Anomaly scores are typically negative for outliers and positive for inliers (around 0).
    # The last dummy data point is an outlier, so its score should be lower.
    assert scores[-1] < scores[0]


# --- Tests for model_utils.py (saving and loading) ---

# Fixture to create and clean up a temporary directory for models
@pytest.fixture
def temp_models_dir(tmp_path):
    # tmp_path is a pytest fixture that provides a unique temporary directory
    return tmp_path / "test_models"

def test_save_and_load_model(temp_models_dir):
    from sklearn.linear_model import LogisticRegression
    dummy_model = LogisticRegression(random_state=42)
    
    # Simulate fitting a model
    X = np.array([[1,2],[3,4],[5,6]])
    y = np.array([0,1,0])
    dummy_model.fit(X,y)

    model_path = temp_models_dir / "test_model.pkl"
    
    model_utils.save_model(dummy_model, str(model_path))
    assert model_path.exists()

    loaded_model = model_utils.load_model(str(model_path))
    assert isinstance(loaded_model, LogisticRegression)
    # Check if the loaded model is the same as the saved one (e.g., coefficients)
    assert np.array_equal(loaded_model.coef_, dummy_model.coef_)


def test_save_and_load_scaler(temp_models_dir):
    from sklearn.preprocessing import StandardScaler
    dummy_scaler = StandardScaler()
    
    # Simulate fitting a scaler
    data_to_fit = np.array([[10], [20], [30]])
    dummy_scaler.fit(data_to_fit)

    scaler_path = temp_models_dir / "test_scaler.pkl"
    
    model_utils.save_scaler(dummy_scaler, str(scaler_path))
    assert scaler_path.exists()

    loaded_scaler = model_utils.load_scaler(str(scaler_path))
    assert isinstance(loaded_scaler, StandardScaler)
    # Check if the loaded scaler's parameters are the same
    assert np.isclose(loaded_scaler.mean_[0], dummy_scaler.mean_[0])
    assert np.isclose(loaded_scaler.scale_[0], dummy_scaler.scale_[0])


def test_load_model_file_not_found(temp_models_dir):
    non_existent_path = temp_models_dir / "non_existent.pkl"
    with pytest.raises(FileNotFoundError, match=f"Model not found at: {non_existent_path}"):
        model_utils.load_model(str(non_existent_path))

def test_load_scaler_file_not_found(temp_models_dir):
    non_existent_path = temp_models_dir / "non_existent_scaler.pkl"
    with pytest.raises(FileNotFoundError, match=f"Scaler not found at: {non_existent_path}"):
        model_utils.load_scaler(str(non_existent_path))

def test_load_model_corrupted_file(temp_models_dir):
    corrupted_path = temp_models_dir / "corrupted_model.pkl"
    # Create a corrupted file (e.g., just some random bytes)
    with open(corrupted_path, 'wb') as f:
        f.write(b'\x01\x02\x03\x04') # Not a valid pickle

    with pytest.raises(IOError, match="Corrupted file or invalid pickle format."):
        model_utils.load_model(str(corrupted_path))

# --- Tests for model_loader.py ---

@patch('src.utils.model_utils.load_model')
def test_model_loader_load_model_success(mock_load_model):
    mock_model_instance = MagicMock()
    mock_load_model.return_value = mock_model_instance
    
    loaded = model_loader.load_model("/fake/path/model.pkl")
    mock_load_model.assert_called_once_with("/fake/path/model.pkl")
    assert loaded is mock_model_instance

@patch('src.utils.model_utils.load_scaler')
def test_model_loader_load_scaler_success(mock_load_scaler):
    mock_scaler_instance = MagicMock()
    mock_load_scaler.return_value = mock_scaler_instance
    
    loaded = model_loader.load_scaler("/fake/path/scaler.pkl")
    mock_load_scaler.assert_called_once_with("/fake/path/scaler.pkl")
    assert loaded is mock_scaler_instance

def test_model_loader_load_model_file_not_found():
    # This will directly call model_utils.load_model which raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        model_loader.load_model("/non/existent/path/model.pkl")

def test_model_loader_load_scaler_file_not_found():
    # This will directly call model_utils.load_scaler which raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        model_loader.load_scaler("/non/existent/path/scaler.pkl")