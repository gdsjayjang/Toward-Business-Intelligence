import streamlit as st

from src.loaders import load_customers
from src.customer_profile import get_customer_profile

st.title('고객 응대 페이지')

data = load_customers()

# 고객 조회
st.write('0000423b00ade91418cceaf3b26c6af3dd342b51fd051eec9c12fb36984420fa')
st.write('ffd7d77fb2d081a05c849bc78a1a1550ff663d7a483bae58ec31923248965e2a')
customer_id = st.text_input('고객 ID 검색')
if not customer_id:
    st.stop()

profile = get_customer_profile(customer_id, data)
if profile is None:
    st.warning('해당 고객의 거래 내역이 없습니다.')
    st.stop()

# 고객 프로필 카드 출력
st.subheader(f'고객 #{customer_id[:10]}...')
# st.caption(f"{profile['age']}세 · {profile['club_member_status']}")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.write("**나이**")
    c1.write(f"{profile['age']}세")

    c2.write("**클럽 멤버**")
    status = profile["club_member_status"]
    if status == 'ACTIVE': 
        c2.write(f':green[**{status}**]')
    elif status == 'LEFT CLUB':
        c2.write(f':red[**{status}**]')
    else:
        c2.write(f':grey[**{status}**]')
    c3.write("**뉴스 수신**")
    c3.write(profile["fashion_news_frequency"])

# RFM
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric('**Recency** (직전 방문)', f'{profile["recency_days"]}일 전')
    c2.metric('**Frequency** (방문 회수)', f'{profile["frequency"]}회')
    c3.metric('**Monetary** (총 구매금액)', f'${profile["monetary"]:.2f}')
