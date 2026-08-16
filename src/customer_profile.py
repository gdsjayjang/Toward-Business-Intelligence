import pandas as pd

def get_customer_profile(customer_id, data):
    row = data.loc[data['customer_id'] == customer_id]
    if row.empty: return None

    r = row.iloc[0]

    return {
        'customer_id': customer_id,
        # RFM
        'recency_days': int(r['days_since_last_purchase']),
        'frequency': int(r['purchase_count']),
        'monetary': float(r['total_spent']),
        # 인구통계
        'age': int(r['age']),
        'club_member_status': r['club_member_status'],
        "fashion_news_frequency": r["fashion_news_frequency"],
        # 세그먼트
        'segment': r['segment']
    }