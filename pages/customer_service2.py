import streamlit as st

from src.loaders import load_customers, cached_talking_points
from src.customer_profile import get_customer_profile
from src.badge import club_status_badge, news_frequency_badge
from src.segments import SEGMENT_COLORS

from src.tagging import memo2tags

st.set_page_config(page_title='고객 응대', page_icon='🧑‍💼', layout='wide')

st.markdown('''
<style>
.tag-chip {
    display: inline-block;
    padding: 4px 14px;
    margin: 4px 6px 0 0;
    border-radius: 999px;
    background-color: rgba(99, 102, 241, 0.15);
    color: #4f46e5;
    font-size: 0.85rem;
    font-weight: 600;
}
@media (prefers-color-scheme: dark) {
    .tag-chip { color: #a5b4fc; }
}
</style>
''', unsafe_allow_html=True)

st.title('🧑‍💼 고객 응대 페이지')
st.caption('고객 ID로 프로필을 조회하고, 응대 메모와 토킹포인트를 생성하세요.')

data = load_customers()

with st.expander('🔧 테스트용 고객 ID (개발용)'):
    st.code(
        '0000423b00ade91418cceaf3b26c6af3dd342b51fd051eec9c12fb36984420fa\n'
        'ffd7d77fb2d081a05c849bc78a1a1550ff663d7a483bae58ec31923248965e2a\n'
        'fff15f528e303627d0dc8b0e9a69fd878a05085b42e72a3688f2c89f1180d979\n'
        '45fec77a87ca372f03b944394b4560580a3bd806a7aa30c6418c909ea3acf98e'
    )

customer_id = st.text_input('🔍 고객 ID 검색', placeholder='고객 ID를 입력하세요...')
if not customer_id:
    st.info('고객 ID를 입력하면 프로필이 표시됩니다.')
    st.stop()

profile = get_customer_profile(customer_id, data)
if profile is None:
    st.warning('해당 고객의 거래 내역이 없습니다.')
    st.stop()

st.divider()

# 고객 프로필 헤더
h1, h2 = st.columns([3, 1])
with h1:
    st.subheader(f'🙍 고객 #{customer_id[:10]}...')
with h2:
    segment_color = SEGMENT_COLORS.get(profile['segment'], 'grey')
    st.markdown(
        f'<div style="text-align:right; padding-top:10px;">'
        f'<span style="color:{segment_color}; font-weight:700;">{profile["segment"]}</span> 고객입니다.'
        f'</div>',
        unsafe_allow_html=True,
    )

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption('🎂 나이')
        st.markdown(f"**{profile['age']}세**")
    with c2:
        st.caption('🎫 클럽 멤버')
        st.markdown(club_status_badge(profile["club_member_status"]))
    with c3:
        st.caption('📰 뉴스 수신')
        st.markdown(news_frequency_badge(profile["fashion_news_frequency"]))

# RFM
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric('🕒 Recency (마지막 방문)', f'{profile["days_since_last_purchase"]}일 전')
    c2.metric('🔁 Frequency (방문 횟수)', f'{profile["purchase_count"]}회')
    c3.metric('💰 Monetary (총 구매금액)', f'${profile["total_spent"]:.2f}')

st.divider()

# 직원 메모 -> 태그
st.subheader('📝 직원 메모')
with st.container(border=True):
    memo = st.text_area(
        '고객 응대 메모',
        key=f'memo_input_{customer_id}',
        placeholder='응대 중 특이사항이나 요청 사항을 기록하세요...',
        label_visibility='collapsed',
    )

    if st.button('🏷️ 태그 생성', type='primary'):
        api_key = st.secrets['GENAI_API_KEY']
        with st.spinner('태그 생성 중...'):
            st.session_state[f'tags_{customer_id}'] = memo2tags(memo, api_key)

    tags = st.session_state.get(f'tags_{customer_id}', [])
    if tags:
        chips = ''.join(f'<span class="tag-chip">#{t}</span>' for t in tags)
        st.markdown(chips, unsafe_allow_html=True)

# 응대 토킹포인트
st.subheader('💬 응대 토킹포인트')
with st.container(border=True):
    if st.button('✨ 토킹포인트 생성', type='primary'):
        st.session_state[f'show_points_{customer_id}'] = True

    if st.session_state.get(f'show_points_{customer_id}'):
        api_key = st.secrets['GENAI_API_KEY']
        points = cached_talking_points(customer_id, tuple(tags), profile, api_key)
        st.markdown(points)
