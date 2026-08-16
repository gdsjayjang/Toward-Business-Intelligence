'''
merged_df를 각 고객에 대해 요약 + RFM 세그먼트 부착
'''
import pandas as pd

# merged_df.csv가 원본
# 나중에 드라이브로 변경하기
df = pd.read_parquet('data/data_clean.parquet')

# 고객 단위 집계
customer_table = df.groupby('customer_id').agg(
    age=('age', 'first'),                    # 고객 속성: 아무 행이나 대표값
    club_member_status=('club_member_status', 'first'),
    fashion_news_frequency=('fashion_news_frequency', 'first'),
    last_purchase=('t_dat', 'max'),             # R, Recency: 마지막 구매 일자
    purchase_count=('t_dat', 'count'),          # F, Frequency: 구매 횟수
    total_spent=('price', 'sum'),               # M, Monetary: 구매 금액
).reset_index()

# 최근성 계산
customer_table['last_purchase'] = pd.to_datetime(customer_table['last_purchase']) # 마지막 거래 날짜
ref_date = customer_table['last_purchase'].max() # 모든 고객 중 가장 최근에 일어난 거래 날짜
customer_table['days_since_last_purchase'] = (ref_date - customer_table['last_purchase']).dt.days # ref_date에서 구매가 얼마동안 안일어났는지

# 저장
customer_table.to_parquet('data/customers_dashboard.parquet', index=False)
print(customer_table.shape)      # (고객수, 열수)
print(customer_table.head())