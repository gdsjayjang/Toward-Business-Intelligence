import streamlit as st

from src.loaders import load_customers, cached_talking_points
from src.customer_profile import get_customer_profile
from src.badge import club_status_badge, news_frequency_badge, segment_badge

from src.tagging import memo2tags

st.title('고객 응대 페이지')

data = load_customers()

# 고객 조회
'''id 체크용'''
st.write('0000423b00ade91418cceaf3b26c6af3dd342b51fd051eec9c12fb36984420fa')
st.write('ffd7d77fb2d081a05c849bc78a1a1550ff663d7a483bae58ec31923248965e2a')
st.write('fff15f528e303627d0dc8b0e9a69fd878a05085b42e72a3688f2c89f1180d979')
st.write('45fec77a87ca372f03b944394b4560580a3bd806a7aa30c6418c909ea3acf98e')


customer_id = st.text_input('고객 ID 검색')
if not customer_id:
    st.stop()

profile = get_customer_profile(customer_id, data)
if profile is None:
    st.warning('해당 고객의 거래 내역이 없습니다.')
    st.stop()

# 고객 프로필
st.subheader(f'고객 #{customer_id[:10]}...')
st.write(f'{segment_badge(profile["segment"])} 고객입니다.')

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.write("**나이**")
    c1.write(f"{profile['age']}세")

    c2.write("**클럽 멤버**")
    c2.write(club_status_badge(profile["club_member_status"]))

    c3.write("**뉴스 수신**")
    c3.write(news_frequency_badge(profile["fashion_news_frequency"]))

# RFM
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric('**Recency** (마지막 방문)', f'{profile["days_since_last_purchase"]}일 전')
    c2.metric('**Frequency** (방문 횟수)', f'{profile["purchase_count"]}회')
    c3.metric('**Monetary** (총 구매금액)', f'${profile["total_spent"]:.2f}')

# 직원 메모 -> 태그
st.subheader('직원 메모')
memo = st.text_area('고객 응대 메모', key=f'memo_input_{customer_id}')

if st.button('태그 생성'):
    api_key = st.secrets['GENAI_API_KEY']
    with st.spinner('태그 생성 중...'):
        st.session_state[f'tags_{customer_id}'] = memo2tags(memo, api_key)

# 저장된 태그 표시 (세션 임시)
tags = st.session_state.get(f'tags_{customer_id}', [])
if tags:
    st.write(' '.join(f'"{t}"' for t in tags))


# 응대 토킹포인트
st.subheader('응대 토킹포인트')

if st.button('토킹포인트 생성'):
    st.session_state[f'show_points_{customer_id}'] = True

if st.session_state.get(f'show_points_{customer_id}'):
    api_key = st.secrets['GENAI_API_KEY']
    points = cached_talking_points(customer_id, tuple(tags), profile, api_key)
    st.info(points)