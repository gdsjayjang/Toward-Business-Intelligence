import pandas as pd

def assign_segments(customers):
    df = customers.copy()
    
    # 4분위 점수화
    # recency: 값이 작을수록 최근 좋음
    # 동점이 많아 경계가 겹치므로 rank로 먼저 순위를 매긴 뒤 4분위 분할
    df['r_score'] = pd.qcut(
        df['days_since_last_purchase'].rank(method="first"), 4, labels=[4, 3, 2, 1]
    ).astype(int)

    # frequency: 값이 클수록 좋음
    # 동점이 많아 경계가 겹치므로 rank로 먼저 순위를 매긴 뒤 4분위 분할
    df['f_score'] = pd.qcut(
        df['purchase_count'].rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)

    # monetary: 값이 클수록 좋음
    df['m_score'] = pd.qcut(
        df['purchase_count'], 4, labels=[1, 2, 3, 4]).astype(int)

    # 세그먼트 규칙
    def label(row):
        '''
        VIP: 세 축 모두 최상위
        이탈위험: 과거 우량인데(F, M 높음), 최근 안 옴(R 낮음)
        충성: 최근에도 자주 오고(R 높음) 자주·많이 사지만 VIP는 아님
        신규: # 최근 왔지만 아직 구매 적음
        나머지 일반
        '''
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r == 4 and f == 4 and m == 4: return "VIP"
        if (f >= 3 or m >= 3) and r <= 2: return "이탈위험"
        if r >= 3 and f >= 3 and m >= 3: return "충성"
        if r >= 3 and f <= 1: return "신규"
        return "일반"

    df["segment"] = df.apply(label, axis=1)

    return df