import os
import pandas as pd

RECENT_ITEMS_PATH = 'data/customer_recent_items.parquet'

def load_raw_customers():
    path = 'data/customers_dashboard.parquet'

    df = pd.read_parquet(path)

    # 최근 구매 상품 유형 (utils/customer_recent_items.py로 생성, 없으면 생략)
    if os.path.exists(RECENT_ITEMS_PATH):
        df = df.merge(pd.read_parquet(RECENT_ITEMS_PATH), on='customer_id', how='left')

    return df
