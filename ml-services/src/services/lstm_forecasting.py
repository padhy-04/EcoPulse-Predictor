# ml-service/src/services/lstm_forecasting.py
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import joblib
import os

class LSTMForecaster:
    """
    LSTM model for time series forecasting.
    Handles data scaling, sequence creation, training, and model persistence.
    """
    def __init__(self, seq_length=10, lstm_units=32, epochs=20, batch_size=16, model_dir='models'):
        self.seq_length = seq_length
        self.lstm_units = lstm_units
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler = None
        self.model_path = os.path.join(model_dir, 'lstm_model.h5')
        self.scaler_path = os.path.join(model_dir, 'lstm_scaler.pkl')
        os.makedirs(model_dir, exist_ok=True) # Ensure model directory exists

    def _build_model(self):
        """Builds the Keras Sequential LSTM model."""
        self.model = Sequential([
            Input(shape=(self.seq_length, 1)),
            LSTM(self.lstm_units, activation='relu'), # Added activation for clarity
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        print("LSTM model architecture built.")

    def create_sequences(self, data: np.ndarray):
        """
        Creates sequences for LSTM training/prediction.

        Parameters:
        - data (np.ndarray): 2D numpy array of scaled time series data.

        Returns:
        - tuple: (X, y) numpy arrays for sequences and targets.
        """
        X, y = [], []
        for i in range(len(data) - self.seq_length):
            X.append(data[i:i + self.seq_length])
            y.append(data[i + self.seq_length])
        return np.array(X), np.array(y)

    def train(self, sensor_data: np.ndarray):
        """
        Trains the LSTM model. Fits the scaler, creates sequences, and trains the model.

        Parameters:
        - sensor_data (np.ndarray): 1D or 2D numpy array of raw sensor values.
        """
        # Ensure data is 2D for scaler
        if sensor_data.ndim == 1:
            sensor_data = sensor_data.reshape(-1, 1)

        print("Fitting MinMaxScaler...")
        self.scaler = MinMaxScaler()
        scaled_data = self.scaler.fit_transform(sensor_data)

        X_lstm, y_lstm = self.create_sequences(scaled_data)

        if len(X_lstm) == 0:
            raise ValueError(f"Not enough data to create sequences with sequence length {self.seq_length}. Need at least {self.seq_length + 1} data points.")

        # Train/test split within the training function for internal validation purposes
        # For production training, you might train on all available data
        split = int(0.8 * len(X_lstm))
        X_train, y_train = X_lstm[:split], y_lstm[:split]

        if self.model is None:
            self._build_model()

        print("Training LSTM model...")
        history = self.model.fit(X_train, y_train, epochs=self.epochs, batch_size=self.batch_size, verbose=1)
        print("LSTM model training complete.")
        self.save_model()
        return history # Optionally return history for plotting loss

    def forecast_next_steps(self, historical_data: np.ndarray, num_steps: int):
        """
        Generates forecasts for the next `num_steps`.

        Parameters:
        - historical_data (np.ndarray): 1D or 2D numpy array of recent historical sensor data.
          This should include enough data to form the initial sequence (at least `seq_length` points).
        - num_steps (int): Number of future steps to forecast.

        Returns:
        - np.ndarray: 1D numpy array of forecasted values in original scale.
        """
        if self.model is None or self.scaler is None:
            self.load_model() # Attempt to load if not already loaded
            if self.model is None or self.scaler is None:
                raise RuntimeError("LSTM model or scaler not loaded. Train or load the model first.")

        if historical_data.ndim == 1:
            historical_data = historical_data.reshape(-1, 1)

        if len(historical_data) < self.seq_length:
            raise ValueError(f"Historical data must be at least {self.seq_length} points long for forecasting.")

        # Scale the historical data
        scaled_history = self.scaler.transform(historical_data).flatten().tolist()
        forecasted_values_scaled = []

        # Initialize current sequence with the last `seq_length` points from scaled history
        current_sequence = scaled_history[-self.seq_length:]

        for _ in range(num_steps):
            # Reshape for LSTM input: (1, seq_length, 1)
            input_seq = np.array(current_sequence[-self.seq_length:]).reshape(1, self.seq_length, 1)
            
            # Predict the next scaled value
            next_scaled_pred = self.model.predict(input_seq, verbose=0)[0, 0]
            
            # Store the prediction
            forecasted_values_scaled.append(next_scaled_pred)
            
            # Add the predicted value to the sequence to use for the next prediction
            current_sequence.append(next_scaled_pred)

        # Inverse transform the scaled predictions to the original scale
        return self.scaler.inverse_transform(np.array(forecasted_values_scaled).reshape(-1, 1)).flatten()

    def save_model(self):
        """Saves the Keras LSTM model and the MinMaxScaler."""
        try:
            self.model.save(self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print(f"LSTM model and scaler saved to {self.model_path} and {self.scaler_path}")
        except Exception as e:
            print(f"Error saving LSTM model/scaler: {e}")
            raise

    def load_model(self):
        """Loads the Keras LSTM model and the MinMaxScaler."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print(f"LSTM model and scaler loaded from {self.model_path} and {self.scaler_path}")
                return True
            else:
                print(f"LSTM model or scaler files not found at {self.model_path} / {self.scaler_path}. Model needs to be trained.")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to load LSTM model or scaler: {e}")
            self.model = None
            self.scaler = None
            raise IOError(f"Corrupted file or invalid format for LSTM model/scaler: {e}")