import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os

DATA_PATH = "training/clean_water_requirement_data.csv"
MODEL_DIR = "AI_model"
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_irrigation_model.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.joblib")

df = pd.read_csv(DATA_PATH)

categorical_columns = [
    "rainfall_pattern",
    "soil_type",
    "drainage_properties",
    "crop_type",
    "growth_stage"
]

feature_columns = [
    "temperature", "humidity", "wind_speed", "evapotranspiration",
    "soil_moisture_levels", "water_retention_capacity",
    "crop_water_requirement", "rainfall_pattern", "soil_type",
    "drainage_properties", "crop_type", "growth_stage"
]
target_column = "water_requirement"

# === Remove outliers using IQR ===
def remove_outliers(df, columns):
    df_out = df.copy()
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_out = df_out[(df_out[col] >= lower_bound) & (df_out[col] <= upper_bound)]
    return df_out

numeric_cols = [
    "temperature", "humidity", "wind_speed", "evapotranspiration",
    "soil_moisture_levels", "water_retention_capacity",
    "crop_water_requirement", "water_requirement"
]
df = remove_outliers(df, numeric_cols)

# === Encode categorical columns ===
label_encoders = {}
for col in categorical_columns:
    encoder = LabelEncoder()
    df[col] = df[col].astype(str)
    df[col] = encoder.fit_transform(df[col])
    label_encoders[col] = encoder

# === Split and train model ===
X = df[feature_columns]
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# === Evaluate ===
y_pred = model.predict(X_test)
print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.2f}")
print(f"R²: {r2_score(y_test, y_pred):.2f}")

# === Save model and encoders ===
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoders, ENCODERS_PATH)

print(f"\n✅ Model saved to: {MODEL_PATH}")
print(f"✅ Encoders saved to: {ENCODERS_PATH}")
