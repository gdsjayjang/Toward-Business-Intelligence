# build_dashboard_data.py  ← 로컬에서 한 번만 실행
import pandas as pd

# 병합된 3천만 행 df를 불러오기 (지금 그 1GB parquet)
df = pd.read_parquet('data/data_clean.parquet')

# 고객 단위로 집계 → 고객당 1행
customer_table = df.groupby('customer_id').agg(
    age=('age', 'first'),                    # 고객 속성: 아무 행이나 대표값
    club_member_status=('club_member_status', 'first'),
    fashion_news_frequency=('fashion_news_frequency', 'first'),
    last_purchase=('t_dat', 'max'),          # RFM
    purchase_count=('t_dat', 'count'),
    total_spent=('price', 'sum'),
).reset_index()

# 최근성 계산
customer_table['last_purchase'] = pd.to_datetime(customer_table['last_purchase'])
ref_date = customer_table['last_purchase'].max()
customer_table['days_since_last_purchase'] = (ref_date - customer_table['last_purchase']).dt.days

# 저장 (이제 수 MB)
customer_table.to_parquet('data/customers_dashboard.parquet', index=False)
print(customer_table.shape)      # (고객수, 열수) — 몇만 행으로 확 줄어듦
print(customer_table.head())