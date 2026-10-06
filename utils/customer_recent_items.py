'''
고객별 최근 구매 상품 유형 집계 (응대 멘트 개인화용)
거래(data_clean) + 상품(articles)을 article_id로 연결해
최근 거래 순으로 중복 없이 최대 3개의 product_type_name을 저장
'''
import sys
import pandas as pd

TX_PATH = sys.argv[1] if len(sys.argv) > 1 else 'data/data_clean.parquet'
ARTICLES_PATH = sys.argv[2] if len(sys.argv) > 2 else 'data/articles.csv'
OUT_PATH = 'data/customer_recent_items.parquet'
TOP_N = 3

tx = pd.read_parquet(TX_PATH, columns=['t_dat', 'customer_id', 'article_id'])
articles = pd.read_csv(ARTICLES_PATH, usecols=['article_id', 'product_type_name'])

df = tx.merge(articles, on='article_id', how='left').dropna(subset=['product_type_name'])
df = df[df['product_type_name'] != 'Unknown']

recent = (
    df.sort_values('t_dat', ascending=False)
    .drop_duplicates(['customer_id', 'product_type_name'])   # 같은 유형은 가장 최근 것만
)
recent = recent[recent.groupby('customer_id').cumcount() < TOP_N]
# 리스트 대신 '|'로 이은 문자열로 저장 (리스트 컬럼은 st.cache_data 복원이 매우 느림)
recent = recent.groupby('customer_id')['product_type_name'].agg('|'.join).rename('recent_items').reset_index()

recent.to_parquet(OUT_PATH, index=False)
print(recent.shape)
print(recent.head())
