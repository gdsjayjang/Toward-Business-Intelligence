import pandas as pd

def get_customer_profile(customer_id, data):
    row = data.loc[data['customer_id'] == customer_id]
    if row.empty: return None

    r = row.iloc[0]

    return {
        'customer_id': customer_id,
        # RFM
        'days_since_last_purchase': int(r['days_since_last_purchase']),
        'purchase_count': int(r['purchase_count']),
        'total_spent': float(r['total_spent']),
        # 인구통계
        'age': int(r['age']),
        'club_member_status': r['club_member_status'],
        "fashion_news_frequency": r["fashion_news_frequency"],
        # 세그먼트
        'segment': r['segment'],
        # 최근 구매 상품 유형 (집계 데이터에 있을 때만)
        'recent_items': r['recent_items'].split('|') if isinstance(r.get('recent_items'), str) else [],
    }