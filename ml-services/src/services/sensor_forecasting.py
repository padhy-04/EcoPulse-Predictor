
# ml-service/src/services/sensor_forecasting.py
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta

# Optional: suppress convergence warnings
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)

def run_forecast(sensor_series=None, steps=30):
    """
    Runs ARIMA time-series forecast on a given sensor series.
    
    Parameters:
    - sensor_series (pd.Series): Time-indexed sensor data. If None, synthetic data is used.
    - steps (int): Number of days to forecast.

    Returns:
    - dict: Contains observed data, forecasted values, and dates.
    """

    # Generate synthetic data if none provided
    if sensor_series is None:
        np.random.seed(42)
        date_rng = pd.date_range(start='2024-01-01', periods=200, freq='D')
        sensor_values = np.cumsum(np.random.randn(200)) + 50
        sensor_series = pd.Series(sensor_values, index=date_rng)

    # Train ARIMA model
    model = ARIMA(sensor_series, order=(2, 1, 2))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)

    forecast_index = pd.date_range(sensor_series.index[-1] + timedelta(days=1), periods=steps, freq='D')

    # Return result as JSON-friendly format
    return {
        "observed": {
            "dates": sensor_series.index.strftime('%Y-%m-%d').tolist(),
            "values": sensor_series.round(2).tolist()
        },
        "forecast": {
            "dates": forecast_index.strftime('%Y-%m-%d').tolist(),
            "values": forecast.round(2).tolist()
        }
    }  