import pandas as pd

from src.segments import SEGMENT_ORDER


def overall_kpis(df: pd.DataFrame) -> dict:
    '''
    대시보드 상단 헤드라인
    '''
    return {
        'total_customers': len(df),
        'avg_monetary': df['total_spent'].mean(),
        'total_monetary': df['total_spent'].sum(),
    }


def segment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    '''
    세그먼트별 고객 수 + 비중
    '''
    dist = (
        df['segment'].value_counts()
        .rename_axis('segment').reset_index(name='count'))
    dist['pct'] = dist['count'] / dist['count'].sum() # 각 세그먼트 비율
    dist['segment'] = pd.Categorical(dist['segment'], categories=SEGMENT_ORDER, ordered=True) # 순서가 있는 범주형변수로 변환

    return dist.sort_values("segment").reset_index(drop=True)


def segment_rfm_summary(df: pd.DataFrame) -> pd.DataFrame:
    '''
    세그먼트별 raw RFM 평균
    '''
    return (
        df.groupby('segment')
        .agg(**{
            '고객 수' : ('segment', 'size'),
            '평균 방문주기' : ('days_since_last_purchase', 'mean'),
            '평균 구매횟수' : ('purchase_count', 'mean'),
            '평균 구매금액' : ('total_spent', 'mean'),}
        )
        .reindex(SEGMENT_ORDER)
        .reset_index()
    )