import streamlit as st

from src.loaders import load_customers
from src import analytics

st.title('경영진 대시보드')

data = load_customers()

# 헤드라인 KPI
# 구매 금액은 월별 구매금액 등으로 변경
kpis = analytics.overall_kpis(data)

c1, c2, c3 = st.columns(3)
c1.metric('전체 고객 수', f'{kpis['total_customers']:,}')
c2.metric('평균 구매금액', f'{kpis['avg_monetary']:,.4f}')
c3.metric('총 구매금액',  f'{kpis['total_monetary']:,.2f}')

# 세그먼트 분포
# 세그먼트 말고 다른 표현
st.subheader("세그먼트 분포")

dist = analytics.segment_distribution(data)

col_chart, col_table = st.columns([2, 1])
with col_chart:
    st.bar_chart(dist.set_index('segment')['count'])
with col_table:
    st.dataframe(
        dist.assign(pct=(dist["pct"] * 100).round(1)),
        hide_index=True,
        column_config={
            'segment': '세그먼트',
            'count': '고객 수',
            'pct': st.column_config.NumberColumn('비중(%)', format='%.1f'),
        },
    )

# 세그먼트별 RFM 요약
st.subheader('세그먼트별 RFM 요약')

rfm = analytics.segment_rfm_summary(data)
st.dataframe(rfm, hide_index=True)