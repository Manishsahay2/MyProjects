import logging
from datetime import datetime
import os
import pandas as pd

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.info("🚀 Pipeline started")

import ctypes

def show_success_popup(message):
    ctypes.windll.user32.MessageBoxW(
        None,                 # No parent window
        message,              # Message text
        "Ecommerce Pipeline Status",  # Title
        0x40                  # Information icon + OK button
    )


import pandas as pd
from pathlib import Path

# Raw data paths
RAW_ORDERS = "C:/Users/Asus/OneDrive/Desktop/estore_project/data/raw/report.csv"
RAW_VLEID = "C:/Users/Asus/OneDrive/Desktop/estore_project/data/raw/estorevle.csv"

# Output paths
OUT_ORDERS_CSV = "data/processed/orders_clean.csv"
OUT_ORDERS_PKL = "data/processed/orders.pkl"
OUT_VLEID_CSV = "data/processed/vleid_clean.csv"

# -----------------------------
# Helper functions
# -----------------------------
def ensure_dirs():
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

def standardize_columns(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

def create_csc_key(df, col='csc_id'):
    """
    Standardizes the CSC ID column:
    - Converts scientific notation to string
    - Strips spaces
    - Removes '.0' from float conversions
    """
    # Convert to string
    df['csc_id_key'] = df[col].apply(lambda x: str(x).strip())
    
    # Remove '.0' if present (from float conversion)
    df['csc_id_key'] = df['csc_id_key'].str.replace('.0','', regex=False)
    
    # Remove invalid or missing values
    df = df[df['csc_id_key'].notna()]
    df = df[df['csc_id_key'] != 'nan']
    
    return df

def convert_csc_to_string(series):
    def convert(x):
        try:
            return str(int(float(x)))
        except:
            return None
    return series.apply(convert)
    


def process_orders():
    print("📥 Processing Orders data...")

    df = pd.read_csv(RAW_ORDERS)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df['csc_id'] = convert_csc_to_string(df['csc_id'])
    df = df[df['csc_id'].notna()]

    df.to_csv(OUT_ORDERS_CSV, index=False)
    df.to_pickle(OUT_ORDERS_PKL)

    print("✅ Orders cleaned & saved")
    return df

def find_csc_column(df):
    possible_cols = [
        'csc_id',
        'csc_code',
        'cscid',
        'csc'
    ]

    for col in possible_cols:
        if col in df.columns:
            return col

    raise KeyError(f"No CSC column found. Available columns: {df.columns.tolist()}")


def process_vleid():
    print("📥 Processing VLE ID data...")

    df = pd.read_csv(RAW_VLEID)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 🔹 Find correct CSC column
    csc_col = find_csc_column(df)

    # 🔹 Standardize column name
    df.rename(columns={csc_col: 'csc_id'}, inplace=True)

    # 🔹 Convert CSC ID
    df['csc_id'] = convert_csc_to_string(df['csc_id'])
    df = df[df['csc_id'].notna()]

    df.to_csv(OUT_VLEID_CSV, index=False)

    print("✅ VLE ID cleaned & saved")
    return df


# -----------------------------
# Main Pipeline
# -----------------------------
import pandas as pd

def run_pipeline():
    """
    Runs the full ETL pipeline: processes orders and VLE ID files,
    ensures directories exist, and returns cleaned dataframes.
    """
    ensure_dirs()  # Make sure processed folder exists
    
    # Process the data
    orders_df = process_orders()
    vleid_df = process_vleid()
    
    # ✅ Confirmation message
    print("\n🎉 Ecommerce ETL pipeline executed successfully!")
    print(f"Orders DataFrame: {orders_df.shape[0]} rows")
    print(f"VLE ID DataFrame: {vleid_df.shape[0]} rows")
    
    # Set pandas display options for clear reading
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', 120)         # Set max width for table
    pd.set_option('display.max_colwidth', 30)   # Truncate long text neatly
    
    # Display first 5 rows of each dataset
    print("\n📄 Sample Orders Data (first 5 rows):")
    display(orders_df.head())
    
    print("\n📄 Sample VLE ID Data (first 5 rows):")
    display(vleid_df.head())

    show_success_popup(
        "✅ Ecommerce pipeline completed successfully!\n\n"
        f"Orders rows: {orders_df.shape[0]}\n"
        f"VLEID rows: {vleid_df.shape[0]}"
    )

    return orders_df, vleid_df


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    run_pipeline()
