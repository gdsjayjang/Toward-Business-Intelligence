import numpy as np
import pandas as pd

def data_loader():
    path = 'data/customers_dashboard.parquet'

    df = pd.read_parquet(path)
    return df