import pandas as pd

def load_raw_customers():
    path = 'data/customers_dashboard.parquet'

    df = pd.read_parquet(path)
    return df