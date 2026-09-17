import streamlit as st

from src.loaders import load_customers
from src import analytics

st.set_page_config(page_title='경영진 대시보드', page_icon='📊', layout='wide')

st.title('📊 경영진 대시보드')
st.caption('전체 고객 현황과 세그먼트별 지표를 한눈에 확인하세요.')

data = load_customers()

st.divider()

# 헤드라인 KPI
# 구매 금액은 월별 구매금액 등으로 변경
st.subheader('🧾 핵심 지표')
kpis = analytics.overall_kpis(data)

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric('👥 전체 고객 수', f'{kpis["total_customers"]:,}')
    c2.metric('💳 평균 구매금액', f'${kpis["avg_monetary"]:,.2f}')
    c3.metric('💰 총 구매금액', f'${kpis["total_monetary"]:,.2f}')

st.divider()

# 세그먼트 분포
st.subheader('🧩 고객 분포')

dist = analytics.segment_distribution(data)

with st.container(border=True):
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.bar_chart(dist.set_index('segment')['count'], color='#4f46e5')
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

st.divider()

# 세그먼트별 RFM 요약
st.subheader('📈 고객 RFM 요약')

with st.container(border=True):
    rfm = analytics.segment_rfm_summary(data)
    st.dataframe(rfm, hide_index=True)