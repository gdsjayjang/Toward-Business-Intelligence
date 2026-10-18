'''
raw CSV 전처리 → merged_df.csv, merged_df.parquet 생성 스크립트

transactions_train.csv 및 customers.csv(구글 드라이브) 전처리 후 customer_id로 병합해
거래 단위 통합 데이터(merged_df)를 생성.
이후 고객 단위 집계는 utils/customers_dashboard.py 에서 수행.

실행:
  python notebooks/4_merged_df.py                      # raw CSV를 구글 드라이브에서 불러올 때 (기본)
  python notebooks/4_merged_df.py --raw-dir <CSV폴더>   # 로컬에 받아둔 raw CSV를 쓸 때
'''
import argparse
import shutil
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'   # 구글 드라이브에서 받은 raw CSV 저장 위치 (재실행 시 재사용)
MERGED_CSV_PATH = DATA_DIR / 'merged_df.csv'
MERGED_PARQUET_PATH = DATA_DIR / 'merged_df.parquet'

# google drive 활용
DRIVE_URL = 'https://drive.usercontent.google.com/download?id={file_ID}&export=download&confirm=t'
transactions_ID = '10jzMeEjNJMSl6yfwGfsKdlZE3RzCeDN3'
customer_ID = '1aQN9gVp5CQeuPaobNkN4339k90zqfvGd'
transaction_url = DRIVE_URL.format(file_ID=transactions_ID)
customer_url = DRIVE_URL.format(file_ID=customer_ID)


def download(url, path):
    # pd.read_csv(url)은 파일 전체를 메모리에 받은 뒤 파싱하므로, 디스크로 스트리밍 저장 후 읽는다
    if path.exists():
        print(f'  이미 있음, 다운로드 생략: {path}')
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.part')
    print(f'  다운로드: {path.name}')
    with urllib.request.urlopen(url) as res, open(tmp, 'wb') as f:
        shutil.copyfileobj(res, f, length=16 * 1024 * 1024)
    tmp.rename(path)
    return path


def preprocess_customers(customers):
    customers = customers.drop(columns='postal_code')
    customers['age'] = customers['age'].fillna(-1).astype('int64')      # 결측 → -1
    customers['FN'] = customers['FN'].fillna(0).astype('bool')          # 1/NaN → True/False
    customers['Active'] = customers['Active'].fillna(0).astype('bool')
    return customers


def preprocess_transactions(transactions_train):
    transactions_train['t_dat'] = pd.to_datetime(transactions_train['t_dat'])
    return transactions_train


def main():
    parser = argparse.ArgumentParser(description='merged_df.csv / merged_df.parquet 생성')
    parser.add_argument('--raw-dir', type=Path, default=None, help='로컬 raw CSV 폴더 (생략 시 구글 드라이브)')
    args = parser.parse_args()

    if args.raw_dir is None:
        print(f'[1/3] raw CSV 로드: 구글 드라이브 → {RAW_DIR} (transactions 약 3.2GB)')
        transactions_src = download(transaction_url, RAW_DIR / 'transactions_train.csv')
        customers_src = download(customer_url, RAW_DIR / 'customers.csv')
    else:
        transactions_src = args.raw_dir / 'transactions_train.csv'
        customers_src = args.raw_dir / 'customers.csv'
        print(f'[1/3] raw CSV 로드: {args.raw_dir}')

    transactions_train = pd.read_csv(transactions_src)
    customers = pd.read_csv(customers_src)

    print('[2/3] 전처리 + 병합')
    customers = preprocess_customers(customers)
    transactions_train = preprocess_transactions(transactions_train)

    # inner = left 동일 (거래 고객 모두 customers에 있으므로)
    merged_df = pd.merge(transactions_train, customers, on='customer_id', how='inner')

    print(f'[3/3] 저장: {MERGED_CSV_PATH}, {MERGED_PARQUET_PATH}')
    merged_df.to_csv(MERGED_CSV_PATH, index=False)
    merged_df.to_parquet(MERGED_PARQUET_PATH, index=False)

    print('shape:', merged_df.shape)
    print(merged_df.dtypes)
    """
    shape: (31788324, 10)
    
    t_dat                     datetime64[us]
    customer_id                          str
    article_id                         int64
    price                            float64
    sales_channel_id                   int64
    FN                                  bool
    Active                              bool
    club_member_status                   str
    fashion_news_frequency               str
    age                                int64
    dtype: object
    """

if __name__ == '__main__':
    main()