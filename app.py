import streamlit as st

from src.loaders import load_customers
from src import analytics
from src.eda import dist_age
from src.badge import segment_badge
from src.segments import SEGMENT_ORDER

st.set_page_config(page_title='고객 데이터 BI 플랫폼', page_icon='🏠', layout='wide')

st.title('🏠 고객 데이터 BI 플랫폼')
st.caption('구매 데이터를 기반으로 고객을 세그먼트화하고, BI 대시보드와 AI 응대 도구를 제공합니다.')

data = load_customers()
kpis = analytics.overall_kpis(data)

st.divider()

# 페이지 안내
st.subheader('🧭 페이지 안내')
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown('#### 🧑‍💼 고객 응대')
        st.caption('고객 ID로 프로필을 조회하고, AI로 응대 메모를 태깅하고 토킹포인트를 생성합니다.')
        st.page_link('pages/customer_service.py', label='고객 응대 페이지로 이동', icon='➡️')
with col2:
    with st.container(border=True):
        st.markdown('#### 📊 경영진 대시보드')
        st.caption('전체 고객 현황과 세그먼트별 지표를 한눈에 확인합니다.')
        st.page_link('pages/executive_bi.py', label='경영진 대시보드로 이동', icon='➡️')

st.divider()

# 세그먼트 안내
st.subheader('🧩 고객 세그먼트 안내')
SEGMENT_DESC = {
    'VIP': 'R·F·M 모두 최상위인 우수 고객',
    '이탈위험': '과거엔 우량했지만 최근 방문이 뜸한 고객',
    '충성': '최근에도 자주, 많이 구매하는 안정적 고객',
    '신규': '최근 유입되었지만 아직 구매 이력이 적은 고객',
    '일반': '위 조건에 해당하지 않는 고객',
}
with st.container(border=True):
    seg_cols = st.columns(len(SEGMENT_ORDER))
    for col, seg in zip(seg_cols, SEGMENT_ORDER):
        with col:
            st.markdown(segment_badge(seg))
            st.caption(SEGMENT_DESC[seg])

st.divider()

# 연령대별 고객 분포
st.subheader('🎂 연령대별 고객 분포')
with st.container(border=True):
    st.bar_chart(dist_age(data), color='#4f46e5')
