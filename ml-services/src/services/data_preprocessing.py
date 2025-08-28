# ml-service/src/services/data_preprocessing.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os # For checking if scaler file exists

# Define the features that your ML model expects.
# This should match the features used during model training.
MONITORED_FEATURES = ['temperature', 'humidity', 'pressure', 'vibration'] # Example features

def dataframe_from_dict(data: dict) -> pd.DataFrame:
    """
    Converts a single dictionary of sensor data into a pandas DataFrame.
    Ensures all MONITORED_FEATURES are present, filling with NaN if missing.
    """
    # Create a DataFrame from the single dictionary
    df = pd.DataFrame([data])

    # Ensure all monitored features are present, adding NaNs for missing ones
    for feature in MONITORED_FEATURES:
        if feature not in df.columns:
            df[feature] = np.nan

    # Reorder columns to ensure consistent feature order
    df = df[MONITORED_FEATURES]
    return df

def dataframe_from_list(data_list: list[dict]) -> pd.DataFrame:
    """
    Converts a list of dictionaries of historical sensor data into a pandas DataFrame.
    Ensures all MONITORED_FEATURES are present.
    """
    if not data_list:
        return pd.DataFrame(columns=MONITORED_FEATURES)

    df = pd.DataFrame(data_list)

    # Ensure all monitored features are present, adding NaNs for missing ones
    for feature in MONITORED_FEATURES:
        if feature not in df.columns:
            df[feature] = np.nan

    # Reorder columns to ensure consistent feature order
    df = df[MONITORED_FEATURES]
    return df

def preprocess_data(data, scaler: StandardScaler = None, train_scaler: bool = False):
    """
    Preprocesses sensor data: converts to DataFrame, handles missing values (simple fill),
    and scales the data.

    Args:
        data (dict or list[dict]): Single sensor data dict or list of historical data dicts.
        scaler (StandardScaler, optional): Pre-trained scaler to use. If None, and train_scaler is True,
                                           a new scaler will be trained.
        train_scaler (bool): If True, a new StandardScaler will be fitted and returned along with
                             the processed data. Requires data to be a list of dicts.

    Returns:
        tuple[np.ndarray, StandardScaler] or np.ndarray:
            - If train_scaler is True: (processed_data_array, fitted_scaler)
            - Otherwise: processed_data_array

    Raises:
        ValueError: If scaler is None and train_scaler is False.
    """
    if isinstance(data, dict):
        df = dataframe_from_dict(data)
    elif isinstance(data, list):
        df = dataframe_from_list(data)
    else:
        raise ValueError("Data must be a dictionary or a list of dictionaries.")

    # Simple imputation: fill missing values with the mean of the column
    # In a real-world scenario, you might use more sophisticated methods
    # For now, let's just make sure there are no NaNs before scaling
    df = df.fillna(df.mean(numeric_only=True))

    if train_scaler:
        if not isinstance(data, list):
            raise ValueError("Training scaler requires a list of historical data.")
        new_scaler = StandardScaler()
        processed_data = new_scaler.fit_transform(df)
        return processed_data, new_scaler
    else:
        if scaler is None:
            raise ValueError("Scaler not provided and train_scaler is False. Cannot preprocess data.")
        processed_data = scaler.transform(df)
        return processed_data

def inverse_transform_data(processed_data: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    """
    Inverse transforms scaled data back to its original scale using the provided scaler.

    Args:
        processed_data (np.ndarray): The scaled data array.
        scaler (StandardScaler): The scaler that was used to transform the data.

    Returns:
        np.ndarray: Data in its original scale.

    Raises:
        ValueError: If scaler is None.
    """
    if scaler is None:
        raise ValueError("Scaler must be provided for inverse transformation.")
    return scaler.inverse_transform(processed_data)