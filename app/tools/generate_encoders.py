import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

CSV_PATH = "training/clean_water_requirement_data.csv"
df = pd.read_csv(CSV_PATH)

categorical_columns = [
    "rainfall_pattern",
    "soil_type",
    "drainage_properties",
    "crop_type",
    "growth_stage"
]

label_encoders = {}

for col in categorical_columns:
    encoder = LabelEncoder()
    df[col] = df[col].astype(str)
    encoder.fit(df[col])
    label_encoders[col] = encoder
    print(f"Fitted encoder for {col}: {list(encoder.classes_)}")

joblib.dump(label_encoders, "AI_model/label_encoders.joblib")

print("label_encoders.joblib saved successfully.")
