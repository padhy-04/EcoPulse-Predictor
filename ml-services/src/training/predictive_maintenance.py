#src/training/predictive_maintenance.py
# Required Libraries
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# XGBoost
from xgboost import XGBClassifier

# SMOTE
from imblearn.over_sampling import SMOTE

# For reproducibility
np.random.seed(42)

# --- 1. Generate Synthetic Data (replace with your real sensor data) ---
n_samples = 2000
X = pd.DataFrame({
    'temperature': np.random.normal(70, 10, n_samples),
    'vibration': np.random.normal(0.5, 0.15, n_samples),
    'pressure': np.random.normal(30, 5, n_samples),
    'humidity': np.random.normal(50, 10, n_samples),
    'rpm': np.random.normal(1500, 300, n_samples),
    'voltage': np.random.normal(220, 10, n_samples),
    'current': np.random.normal(10, 2, n_samples),
    'sound_level': np.random.normal(70, 5, n_samples),
    'oil_quality': np.random.uniform(0, 1, n_samples),
    'load': np.random.uniform(50, 100, n_samples)
})

# Simulate failures: more likely at high temp, vibration, load, and low oil quality
failure_prob = (
    0.02 +
    0.02 * (X['temperature'] > 85) +
    0.03 * (X['vibration'] > 0.7) +
    0.03 * (X['oil_quality'] < 0.2) +
    0.02 * (X['load'] > 90)
)
y = (np.random.rand(n_samples) < failure_prob).astype(int)
X['failure'] = y

# --- 2. Preprocessing ---
features = [c for c in X.columns if c != 'failure']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[features])

# --- 3. Train-Test Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, X['failure'], test_size=0.2, stratify=X['failure'], random_state=42
)

# --- 4. Apply SMOTE to Training Data Only ---
sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

# --- 5. Model Training & Evaluation ---

def print_results(model_name, y_true, y_pred):
    print(f"\n{model_name} Results (with SMOTE):")
    print(classification_report(y_true, y_pred, digits=4))
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_res, y_train_res)
rf_pred = rf.predict(X_test)
print_results("Random Forest", y_test, rf_pred)

# Gradient Boosting
gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb.fit(X_train_res, y_train_res)
gb_pred = gb.predict(X_test)
print_results("Gradient Boosting", y_test, gb_pred)

# XGBoost (updated: removed deprecated use_label_encoder param)
xgb = XGBClassifier(n_estimators=100, eval_metric='logloss', random_state=42)
xgb.fit(X_train_res, y_train_res)
xgb_pred = xgb.predict(X_test)
print_results("XGBoost", y_test, xgb_pred)
