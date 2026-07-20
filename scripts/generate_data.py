from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Initialize Faker
fake = Faker("en_IN")

# Project folders
RAW_DATA_PATH = Path("data/raw")
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

# Configuration
NUM_DAYS = 15
ROWS_PER_DAY = 1000

# Master Data
WAREHOUSES = [
    "Delhi_WH01",
    "Mumbai_WH02",
    "Bengaluru_WH03",
    "Hyderabad_WH04",
    "Chennai_WH05"
]

CARRIERS = [
    "DHL",
    "FedEx",
    "Blue Dart",
    "Delhivery",
    "Ecom Express"
]

VEHICLES = [
    "Bike",
    "Van",
    "Mini Truck",
    "Truck"
]

STATUS = [
    "Delivered",
    "In Transit",
    "Delayed",
    "Cancelled",
    "Returned"
]# -------------------------------
# Master Cities
# -------------------------------

CITIES = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Lucknow"
]


def generate_record(shipment_no, shipment_date):
    origin = random.choice(CITIES)

    destination = random.choice(
        [city for city in CITIES if city != origin]
    )

    weight = round(random.uniform(0.5, 50), 2)

    distance = random.randint(50, 2500)

    shipping_cost = round(
        80 + (weight * 12) + (distance * 1.8),
        2
    )

    return {
        "shipment_id": f"SHP{shipment_no:06}",
        "order_id": f"ORD{100000 + shipment_no}",
        "customer_id": f"CUST{random.randint(1000,9999)}",
        "shipment_date": shipment_date.strftime("%Y-%m-%d"),
        "warehouse": random.choice(WAREHOUSES),
        "origin_city": origin,
        "destination_city": destination,
        "carrier": random.choice(CARRIERS),
        "vehicle_type": random.choice(VEHICLES),
        "weight_kg": weight,
        "distance_km": distance,
        "shipping_cost": shipping_cost,
        "status": random.choices(
            STATUS,
            weights=[70,20,5,3,2],
            k=1
        )[0]
    }# -------------------------------
# Generate 15 Days Data
# -------------------------------

start_date = datetime(2026, 7, 1)

shipment_counter = 1

for day in range(NUM_DAYS):

    current_date = start_date + timedelta(days=day)

    records = []

    for _ in range(ROWS_PER_DAY):

        records.append(
            generate_record(
                shipment_counter,
                current_date
            )
        )

        shipment_counter += 1

    df = pd.DataFrame(records)

    file_name = f"shipments_{current_date.strftime('%Y_%m_%d')}.csv"

    file_path = RAW_DATA_PATH / file_name

    df.to_csv(file_path, index=False)

    print(f"Generated : {file_name} ({len(df)} records)")

print("\n✅ All 15 days logistics data generated successfully.")

# ---------------------------------
# Carrier Master File
# ---------------------------------

carrier_master = pd.DataFrame({
    "carrier_id": ["C001","C002","C003","C004","C005"],
    "carrier_name": ["DHL","FedEx","Blue Dart","Delhivery","Ecom Express"],
    "service_tier": ["Premium","Premium","Standard","Economy","Economy"],
    "valid_from": ["2026-07-01"] * 5,
    "is_current": [True] * 5
})

carrier_master.to_csv(
    RAW_DATA_PATH / "carrier_master.csv",
    index=False
)

print("Generated : carrier_master.csv")

# ---------------------------------
# Warehouse Master File
# ---------------------------------

warehouse_master = pd.DataFrame({
    "warehouse_id": ["W001","W002","W003","W004","W005"],
    "warehouse_name": [
        "Delhi_WH01",
        "Mumbai_WH02",
        "Bengaluru_WH03",
        "Hyderabad_WH04",
        "Chennai_WH05"
    ],
    "region": [
        "North",
        "West",
        "South",
        "South",
        "South"
    ],
    "valid_from": ["2026-07-01"] * 5,
    "is_current": [True] * 5
})

warehouse_master.to_csv(
    RAW_DATA_PATH / "warehouse_master.csv",
    index=False
)

print("Generated : warehouse_master.csv")

# ---------------------------------
# Carrier Master Update (Mid-stream Change)
# ---------------------------------

carrier_master_update = pd.DataFrame({
    "carrier_id": ["C003"],
    "carrier_name": ["Blue Dart"],
    "service_tier": ["Premium"],
    "valid_from": ["2026-07-08"],
    "is_current": [True]
})

carrier_master_update.to_csv(
    RAW_DATA_PATH / "carrier_master_update.csv",
    index=False
)

print("Generated : carrier_master_update.csv")

# ---------------------------------
# Warehouse Master Update (Mid-stream Change)
# ---------------------------------

warehouse_master_update = pd.DataFrame({
    "warehouse_id": ["W002"],
    "warehouse_name": ["Mumbai_WH02_New"],
    "region": ["West"],
    "valid_from": ["2026-07-10"],
    "is_current": [True]
})

warehouse_master_update.to_csv(
    RAW_DATA_PATH / "warehouse_master_update.csv",
    index=False
)

print("Generated : warehouse_master_update.csv")

# ---------------------------------
# Inject Data Quality Issues
# ---------------------------------

# 1. Duplicate records in Day 1
df = pd.read_csv(RAW_DATA_PATH / "shipments_2026_07_01.csv")
df = pd.concat([df, df.iloc[:10]], ignore_index=True)
df.to_csv(RAW_DATA_PATH / "shipments_2026_07_01.csv", index=False)

print("Injected duplicate records into Day 1")

# 2. Missing customer_id in Day 2
df = pd.read_csv(RAW_DATA_PATH / "shipments_2026_07_02.csv")
df.loc[:19, "customer_id"] = None
df.to_csv(RAW_DATA_PATH / "shipments_2026_07_02.csv", index=False)

print("Injected missing customer_id into Day 2")

# 3. Inconsistent currency_code in Day 3
df = pd.read_csv(RAW_DATA_PATH / "shipments_2026_07_03.csv")

df["currency_code"] = "INR"

df.loc[:10, "currency_code"] = "inr"
df.loc[11:20, "currency_code"] = "Inr"

df.to_csv(RAW_DATA_PATH / "shipments_2026_07_03.csv", index=False)

print("Injected inconsistent currency_code into Day 3")

# 4. Incorrect exception_flag in Day 4
df = pd.read_csv(RAW_DATA_PATH / "shipments_2026_07_04.csv")

df["exception_flag"] = df["status"] != "Delivered"

# Intentionally make some incorrect
df.loc[:15, "exception_flag"] = False

df.to_csv(RAW_DATA_PATH / "shipments_2026_07_04.csv", index=False)

print("Injected incorrect exception_flag into Day 4")

# 5. Remove customer_id column from Day 5
df = pd.read_csv(RAW_DATA_PATH / "shipments_2026_07_05.csv")

df.drop(columns=["customer_id"], inplace=True)

df.to_csv(
    RAW_DATA_PATH / "shipments_2026_07_05.csv",
    index=False
)

print("Injected missing column into Day 5")