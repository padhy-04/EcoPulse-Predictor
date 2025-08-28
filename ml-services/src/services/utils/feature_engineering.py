#services/utils/feature_engineering.py
import pandas as pd
import numpy as np

def create_time_features(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
    """
    Creates time-based features from a timestamp column.

    Args:
        df (pd.DataFrame): DataFrame with a timestamp column.
        timestamp_col (str): Name of the column containing timestamps.

    Returns:
        pd.DataFrame: DataFrame with added time features.
    """
    if timestamp_col not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_col}' not found in DataFrame.")

    # Ensure the timestamp column is in datetime format
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    df['hour_of_day'] = df[timestamp_col].dt.hour
    df['day_of_week'] = df[timestamp_col].dt.dayofweek # Monday=0, Sunday=6
    df['day_of_month'] = df[timestamp_col].dt.day
    df['month'] = df[timestamp_col].dt.month
    df['year'] = df[timestamp_col].dt.year
    df['quarter'] = df[timestamp_col].dt.quarter
    df['is_weekend'] = (df[timestamp_col].dt.dayofweek >= 5).astype(int) # 1 for weekend, 0 for weekday

    return df

def create_lag_features(df: pd.DataFrame, features: list[str], lags: list[int]) -> pd.DataFrame:
    """
    Creates lagged features for specified columns.

    Args:
        df (pd.DataFrame): DataFrame with numerical features.
        features (list[str]): List of column names to create lag features for.
        lags (list[int]): List of lag periods (e.g., [1, 2, 24] for 1, 2, 24 previous values).

    Returns:
        pd.DataFrame: DataFrame with added lag features.
    """
    for feature in features:
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame for lag creation.")
        for lag in lags:
            df[f'{feature}_lag_{lag}'] = df[feature].shift(lag)
    return df

def create_rolling_features(df: pd.DataFrame, features: list[str], windows: list[int], aggregations: list[str]) -> pd.DataFrame:
    """
    Creates rolling window features (e.g., moving average, standard deviation).

    Args:
        df (pd.DataFrame): DataFrame with numerical features.
        features (list[str]): List of column names to create rolling features for.
        windows (list[int]): List of window sizes (e.g., [3, 24] for 3-hour/24-hour windows).
        aggregations (list[str]): List of aggregation functions ('mean', 'std', 'min', 'max', 'sum').

    Returns:
        pd.DataFrame: DataFrame with added rolling features.
    """
    for feature in features:
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame for rolling features.")
        for window in windows:
            # min_periods allows earlier rows to have features, which is good for initial data points
            rolling_window = df[feature].rolling(window=window, min_periods=1)
            for agg_func in aggregations:
                if agg_func == 'mean':
                    df[f'{feature}_rolling_mean_{window}'] = rolling_window.mean()
                elif agg_func == 'std':
                    df[f'{feature}_rolling_std_{window}'] = rolling_window.std()
                elif agg_func == 'min':
                    df[f'{feature}_rolling_min_{window}'] = rolling_window.min()
                elif agg_func == 'max':
                    df[f'{feature}_rolling_max_{window}'] = rolling_window.max()
                elif agg_func == 'sum':
                    df[f'{feature}_rolling_sum_{window}'] = rolling_window.sum()
                else:
                    print(f"Warning: Aggregation function '{agg_func}' not supported.")
    return df

def apply_all_feature_engineering(df: pd.DataFrame, timestamp_col: str, numerical_features: list[str]) -> pd.DataFrame:
    """
    Applies a common set of feature engineering steps.

    Args:
        df (pd.DataFrame): Input DataFrame.
        timestamp_col (str): Name of the timestamp column.
        numerical_features (list[str]): List of numerical features to apply lags/rolling to.

    Returns:
        pd.DataFrame: DataFrame with all engineered features, dropping original timestamp if desired.
    """
    # Create a single copy at the beginning to avoid SettingWithCopyWarning and improve efficiency
    processed_df = df.copy()

    # Ensure timestamp column is first for sorting if necessary for rolling/lags
    if timestamp_col in processed_df.columns:
        processed_df = processed_df.sort_values(by=timestamp_col).reset_index(drop=True)

    # 1. Create time-based features
    # Pass processed_df directly; create_time_features will modify it in place
    processed_df = create_time_features(processed_df, timestamp_col=timestamp_col)

    # 2. Create lag features (example lags: 1, 2, 3 periods back)
    # Pass processed_df directly; create_lag_features will modify it in place
    processed_df = create_lag_features(processed_df, features=numerical_features, lags=[1, 2, 3])

    # 3. Create rolling features (example windows: 3, 6, 12, 24 periods)
    # Pass processed_df directly; create_rolling_features will modify it in place
    processed_df = create_rolling_features(processed_df, features=numerical_features, windows=[3, 6, 12, 24], aggregations=['mean', 'std'])

    # Drop rows with NaN values created by lag/rolling features at the beginning of the series
    processed_df = processed_df.dropna()

    # You might drop the original timestamp column if its derivatives are enough
    # processed_df = processed_df.drop(columns=[timestamp_col])

    return processed_df

# Example Usage (for testing/demonstration)
if __name__ == '__main__':
    # Create some dummy sensor data
    data = [
        {'timestamp': '2023-01-01 00:00:00', 'temperature': 20.0, 'humidity': 50.0, 'pressure': 1000},
        {'timestamp': '2023-01-01 01:00:00', 'temperature': 21.0, 'humidity': 51.0, 'pressure': 1001},
        {'timestamp': '2023-01-01 02:00:00', 'temperature': 22.0, 'humidity': 52.0, 'pressure': 1002},
        {'timestamp': '2023-01-01 03:00:00', 'temperature': 21.5, 'humidity': 51.5, 'pressure': 1001},
        {'timestamp': '2023-01-01 04:00:00', 'temperature': 23.0, 'humidity': 53.0, 'pressure': 1003},
        {'timestamp': '2023-01-01 05:00:00', 'temperature': 24.0, 'humidity': 54.0, 'pressure': 1004},
        {'timestamp': '2023-01-01 06:00:00', 'temperature': 23.5, 'humidity': 53.5, 'pressure': 1003},
        {'timestamp': '2023-01-01 07:00:00', 'temperature': 25.0, 'humidity': 55.0, 'pressure': 1005},
    ]
    df = pd.DataFrame(data)

    numerical_cols = ['temperature', 'humidity', 'pressure']

    print("Original DataFrame:")
    print(df)

    # Use the apply_all_feature_engineering without .copy() in the call here,
    # as the function itself handles the initial copy.
    engineered_df = apply_all_feature_engineering(df, 'timestamp', numerical_cols)

    print("\nDataFrame after Feature Engineering:")
    print(engineered_df.head())
    print(engineered_df.columns.tolist())
    print(engineered_df.shape)