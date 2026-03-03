import pandas as pd
import numpy as np
import hashlib
import glob
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------------
# Utility: Ensure output folder exists
# -------------------------------
def ensure_output_folder(folder="output"):
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.info(f"Created output folder: {folder}")

# -------------------------------
# Step 1: Extract
# -------------------------------
def extract_data(raw_folder="C:/Users/cjgoh/PycharmProjects/HDB-V1/raw_data"):
    files = glob.glob(f"{raw_folder}/*.csv")
    if not files:
        raise FileNotFoundError(f"No CSV files found in {raw_folder}")
    logging.info(f"Extracted {len(files)} files")
    dfs = [pd.read_csv(f) for f in files]
    master = pd.concat(dfs, ignore_index=True)
    logging.info(f"Total rows: {len(master)}")
    return master

# -------------------------------
# Step 2: Profile
# -------------------------------
def profile_data(df):
    logging.info("Data profiling summary:")
    logging.info(df.describe(include="all"))
    logging.info(f"Missing values:\n{df.isnull().sum()}")
    return df

# -------------------------------
# Step 3: Validation
# -------------------------------
def validate_data(df):
    valid_towns = df["town"].unique()  # assume all towns in dataset are valid
    df = df[df["town"].isin(valid_towns)]
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df = df.dropna(subset=["month"])
    return df

# -------------------------------
# Step 4: Remaining Lease
# -------------------------------
def compute_remaining_lease(df):
    today = datetime.today()
    df["lease_commence_date"] = pd.to_datetime(df["lease_commence_date"], format="%Y", errors="coerce")
    df["remaining_lease_years"] = 99 - (today.year - df["lease_commence_date"].dt.year)
    df["remaining_lease_months"] = (99*12) - ((today.year - df["lease_commence_date"].dt.year)*12 + today.month)
    return df

# -------------------------------
# Step 5: Deduplication
# -------------------------------
def deduplicate(df):
    df = df.sort_values("resale_price", ascending=False)
    df = df.drop_duplicates(subset=[col for col in df.columns if col != "resale_price"], keep="first")
    return df

# -------------------------------
# Step 6: Anomaly Detection
# -------------------------------
def detect_anomalies(df):
    df["zscore"] = (df["resale_price"] - df["resale_price"].mean()) / df["resale_price"].std()
    anomalies = df[df["zscore"].abs() > 3]
    logging.info(f"Detected {len(anomalies)} anomalies")
    anomalies.to_csv("output/failed_anomalies.csv", index=False)
    return anomalies

# -------------------------------
# Step 7: Transformation
# -------------------------------
def create_resale_identifier(df):
    df["year_month"] = df["month"].dt.to_period("M")
    group_avg = (
        df.groupby(["year_month", "town", "flat_type"])["resale_price"]
        .mean()
        .reset_index()
    )
    group_avg["avg_prefix"] = group_avg["resale_price"].astype(int).astype(str).str[:2]

    df = df.merge(group_avg[["year_month", "town", "flat_type", "avg_prefix"]],
                  on=["year_month", "town", "flat_type"], how="left")

    def identifier(row):
        block = "".join([c for c in str(row["block"]) if c.isdigit()]).zfill(3)[:3]
        avg_price_prefix = row["avg_prefix"] if pd.notnull(row["avg_prefix"]) else "00"
        month_digits = row["month"].strftime("%m")
        town_char = row["town"][0].upper()
        return f"S{block}{avg_price_prefix}{month_digits}{town_char}"

    df["resale_identifier"] = df.apply(identifier, axis=1)
    return df

# -------------------------------
# Step 8: Hash Identifier
# -------------------------------
def hash_identifier(df):
    df["hashed_id"] = df["resale_identifier"].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
    return df

# -------------------------------
# Step 9: Export
# -------------------------------
def export_data(raw, cleaned, transformed, hashed, failed, folder="output"):
    raw.to_csv(f"{folder}/raw_master.csv", index=False)
    cleaned.to_csv(f"{folder}/cleaned.csv", index=False)
    transformed.to_csv(f"{folder}/transformed.csv", index=False)
    hashed.to_csv(f"{folder}/hashed.csv", index=False)
    failed.to_csv(f"{folder}/failed.csv", index=False)
    logging.info("Exported all datasets")

# -------------------------------
# Pipeline Runner
# -------------------------------
def run_pipeline():
    ensure_output_folder("output")
    raw = extract_data()
    profiled = profile_data(raw)
    validated = validate_data(profiled)
    leased = compute_remaining_lease(validated)
    deduped = deduplicate(leased)
    anomalies = detect_anomalies(deduped)
    transformed = create_resale_identifier(deduped)
    hashed = hash_identifier(transformed)
    export_data(raw, deduped, transformed, hashed, anomalies)

# Run pipeline
if __name__ == "__main__":
    run_pipeline()
