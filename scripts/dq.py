import pandas as pd

REQUIRED_COLUMNS = [
    "shipment_id",
    "customer_id",
    "shipment_date",
    "warehouse",
    "carrier",
    "weight_kg",
    "shipping_cost"
]


def check_required_columns(df):

    missing = []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing.append(col)

    return missing

def remove_duplicate_shipments(df):

    before = len(df)

    df = df.drop_duplicates(subset=["shipment_id"])

    removed = before - len(df)

    return df, removed


def remove_missing_customer(df):

    before = len(df)

    df = df[df["customer_id"].notna()]

    removed = before - len(df)

    return df, removed


def remove_negative_weight(df):

    before = len(df)

    df = df[df["weight_kg"] >= 0]

    removed = before - len(df)

    return df, removed


def validate_master_data(df, warehouse_map, carrier_map):

    before = len(df)

    df = df[
        df["warehouse"].isin(warehouse_map.keys())
    ]

    df = df[
        df["carrier"].isin(carrier_map.keys())
    ]

    removed = before - len(df)

    return df, removed

from dq import (
    check_required_columns,
    remove_duplicate_shipments,
    remove_missing_customer,
    remove_negative_weight,
    validate_master_data
)