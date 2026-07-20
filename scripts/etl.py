import os
import glob
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

from api.freight_api import get_rate_with_retry, apply_fuel_surcharge

# Logging Setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# PostgreSQL Connection
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Read all CSV files from RAW_DATA_PATH
DATA_FOLDER = os.getenv("RAW_DATA_PATH")
csv_files = sorted(glob.glob(os.path.join(DATA_FOLDER, "*.csv")))

shipment_files = [f for f in csv_files if os.path.basename(f).startswith("shipments_")]

print(f"Found {len(shipment_files)} files")
logging.info(f"Found {len(shipment_files)} files")

# Master Mappings
warehouse_map = {
    "Delhi_WH01": 1,
    "Mumbai_WH02": 2,
    "Bengaluru_WH03": 3,
    "Hyderabad_WH04": 4,
    "Chennai_WH05": 5
}

carrier_map = {
    "DHL": 1,
    "FedEx": 2,
    "Blue Dart": 3,
    "Delhivery": 4,
    "Ecom Express": 5
}

# ----------------------------------------
# Process Each CSV File
# ----------------------------------------
for file_path in shipment_files:
    file_name = os.path.basename(file_path)

    # 1. Idempotency Check: Skip if already processed
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM logistics.processed_files WHERE file_name=:file"),
            {"file": file_name}
        )
        if result.scalar() > 0:
            print(f"Skipping already processed: {file_name}")
            continue

    print(f"Processing: {file_name}")
    df = pd.read_csv(file_path)
    rows_read = len(df)

    # 2. Data Quality Checks (Point 4)
    # Required columns check (Reject file if missing)
    required_cols = [
        "shipment_id", "shipment_date", "warehouse", "carrier", 
        "customer_id", "destination_city", "vehicle_type", 
        "weight_kg", "shipping_cost", "status"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Rejecting file {file_name} due to missing columns: {missing_cols}")
        logging.warning(f"Rejecting file {file_name} due to missing columns: {missing_cols}")
        continue

    # Auto-correct duplicates based on shipment_id
    initial_len = len(df)
    df = df.drop_duplicates(subset=["shipment_id"])
    duplicate_removed = initial_len - len(df)

    # Reject missing customer_id
    initial_len = len(df)
    df = df.dropna(subset=["customer_id"])
    customer_removed = initial_len - len(df)

    # Reject negative weights
    initial_len = len(df)
    df = df[df["weight_kg"] >= 0]
    weight_removed = int(initial_len - len(df))

    # Quarantine invalid master data (warehouses or carriers not in mapping)
    initial_len = len(df)
    df = df[df["warehouse"].isin(warehouse_map.keys()) & df["carrier"].isin(carrier_map.keys())]
    master_removed = int(initial_len - len(df))

    # 3. Transformations & API Integration
    df["shipment_date"] = pd.to_datetime(df["shipment_date"])
    df["warehouse_key"] = df["warehouse"].map(warehouse_map)
    df["carrier_key"] = df["carrier"].map(carrier_map)

    if "currency_code" not in df.columns:
        df["currency_code"] = "INR"
    df["currency_code"] = df["currency_code"].fillna("INR").str.upper()

    # Get exchange rate and apply fuel surcharge
    df["exchange_rate"] = df["currency_code"].apply(get_rate_with_retry)
    df["freight_cost_local"] = df["shipping_cost"].apply(apply_fuel_surcharge)
    df["freight_cost_usd"] = round(df["freight_cost_local"] / df["exchange_rate"], 2)
    
    df["exception_flag"] = df["status"] != "Delivered"
    df["date_key"] = df["shipment_date"].dt.date

    # Prepare Fact Table DataFrame
    fact_df = pd.DataFrame({
        "shipment_id": df["shipment_id"],
        "warehouse_key": df["warehouse_key"],
        "carrier_key": df["carrier_key"],
        "date_key": df["date_key"],
        "customer_id": df["customer_id"],
        "destination_code": df["destination_city"],
        "service_level": df["vehicle_type"],
        "weight_kg": df["weight_kg"],
        "freight_cost_local": df["shipping_cost"],
        "currency_code": df["currency_code"],
        "freight_cost_usd": df["freight_cost_usd"],
        "exception_flag": df["exception_flag"],
        "ship_timestamp": df["shipment_date"],
        "source_file": file_name,
        "load_batch_id": file_name.replace(".csv", "")
    })

    # 4. Load Fact Data into PostgreSQL
    fact_df.to_sql(
        "fact_shipment",
        engine,
        schema="logistics",
        if_exists="append",
        index=False,
        method="multi"
    )

    # 5. Record Processed File and DQ Summary per run
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO logistics.processed_files (file_name, processed_at, row_count)
                VALUES (:file_name, NOW(), :row_count)
            """),
            {"file_name": file_name, "row_count": len(fact_df)}
        )

        conn.execute(
            text("""
                INSERT INTO logistics.dq_run_summary
                (
                    source_file,
                    rows_read,
                    rows_loaded,
                    rows_quarantined,
                    rows_rejected,
                    rows_autocorrected
                )
                VALUES
                (
                    :source_file,
                    :rows_read,
                    :rows_loaded,
                    :rows_quarantined,
                    :rows_rejected,
                    :rows_autocorrected
                )
            """),
            {
                "source_file": file_name,
                "rows_read": rows_read,
                "rows_loaded": len(fact_df),
                "rows_quarantined": master_removed,
                "rows_rejected": customer_removed + weight_removed,
                "rows_autocorrected": duplicate_removed
            }
        )

    print(f"Successfully Loaded: {file_name}")
    logging.info(f"Successfully Loaded: {file_name}")

print("\n===================================")
print("ETL COMPLETED SUCCESSFULLY")
print("===================================")
logging.info("ETL COMPLETED SUCCESSFULLY")