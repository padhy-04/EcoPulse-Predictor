#services/utils/model_utils.py
import joblib # Changed from pickle to joblib
import os

def save_model(model, path: str):
    """
    Saves a trained scikit-learn model (or any picklable Python object) using joblib.

    Args:
        model: The model or object to save.
        path (str): The full path including filename to save the model to.

    Raises:
        IOError: If there's an issue writing the file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True) # Ensure directory exists
    try:
        joblib.dump(model, path) # Using joblib.dump
        print(f"Model saved successfully to {path}")
    except Exception as e:
        raise IOError(f"Error saving model to {path}: {e}")

def load_model(path: str):
    """
    Loads a trained scikit-learn model (or any picklable Python object) from a file using joblib.

    Args:
        path (str): The full path including filename of the model to load.

    Returns:
        The loaded model object.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        IOError: If there's an issue reading or unpickling the file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at: {path}")

    try:
        model = joblib.load(path) # Using joblib.load
        print(f"Model loaded successfully from {path}")
        return model
    except Exception as e: # joblib.load can raise various exceptions
        raise IOError(f"Error loading model from {path}: Corrupted file or invalid format. {e}")


def save_scaler(scaler, path: str):
    """
    Saves a fitted scikit-learn scaler (or any picklable Python object) using joblib.

    Args:
        scaler: The scaler or object to save.
        path (str): The full path including filename to save the scaler to.

    Raises:
        IOError: If there's an issue writing the file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True) # Ensure directory exists
    try:
        joblib.dump(scaler, path) # Using joblib.dump
        print(f"Scaler saved successfully to {path}")
    except Exception as e:
        raise IOError(f"Error saving scaler to {path}: {e}")


def load_scaler(path: str):
    """
    Loads a fitted scikit-learn scaler (or any picklable Python object) from a file using joblib.

    Args:
        path (str): The full path including filename of the scaler to load.

    Returns:
        The loaded scaler object.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        IOError: If there's an issue reading or unpickling the file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Scaler not found at: {path}")

    try:
        scaler = joblib.load(path) # Using joblib.load
        print(f"Scaler loaded successfully from {path}")
        return scaler
    except Exception as e:
        raise IOError(f"Error loading scaler from {path}: Corrupted file or invalid format. {e}")

# Example Usage (for testing/demonstration)
if __name__ == '__main__':
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import MinMaxScaler

    # Create dummy model and scaler
    dummy_model = RandomForestClassifier(random_state=42)
    dummy_scaler = MinMaxScaler()

    # Define paths
    test_models_dir = 'temp_test_models'
    test_model_path = os.path.join(test_models_dir, 'dummy_model.pkl')
    test_scaler_path = os.path.join(test_models_dir, 'dummy_scaler.pkl')

    # Test saving
    try:
        save_model(dummy_model, test_model_path)
        save_scaler(dummy_scaler, test_scaler_path)
    except IOError as e:
        print(f"Error during save test: {e}")

    # Test loading
    try:
        loaded_model = load_model(test_model_path)
        loaded_scaler = load_scaler(test_scaler_path)

        print(f"Loaded Model Type: {type(loaded_model)}")
        print(f"Loaded Scaler Type: {type(loaded_scaler)}")

        assert isinstance(loaded_model, RandomForestClassifier)
        assert isinstance(loaded_scaler, MinMaxScaler)
        print("Model and Scaler loaded successfully and are of correct type.")

    except (FileNotFoundError, IOError) as e:
        print(f"Error during load test: {e}")

    # Test file not found
    try:
        load_model(os.path.join(test_models_dir, 'non_existent_model.pkl'))
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")

    # Clean up dummy files
    if os.path.exists(test_model_path):
        os.remove(test_model_path)
    if os.path.exists(test_scaler_path):
        os.remove(test_scaler_path)
    if os.path.exists(test_models_dir):
        os.rmdir(test_models_dir)