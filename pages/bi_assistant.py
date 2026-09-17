import streamlit as st

from src import rag
from src.loaders import load_customers

st.set_page_config(page_title='BI 어시스턴트', page_icon='🤖', layout='wide')

st.title('🤖 BI 어시스턴트 (RAG)')
st.caption('세그먼트 정의·지표 정의·데이터 사전 등 사내 문서에 근거해 답변하고 출처를 표시합니다.')

with st.expander('💡 질문 예시'):
    st.markdown(
        '- 충성 세그먼트 기준이 뭐야?\n'
        '- 재구매율은 어떻게 계산해?\n'
        '- VIP와 충성의 차이는?\n'
        '- 신규 세그먼트에는 어떤 전략을 써야 해?\n'
        '- 전체 고객 수는 몇 명이야? *(→ 데이터 조회로 자동 라우팅)*'
    )

st.divider()

data = load_customers()
api_key = st.secrets['GENAI_API_KEY']

st.session_state.setdefault('rag_history', [])

for msg in st.session_state.rag_history:
    with st.chat_message(msg['role']):
        if msg.get('mode'):
            st.caption(msg['mode'])
        st.markdown(msg['content'])
        if msg.get('sources'):
            with st.expander(f"📎 출처 ({len(msg['sources'])})"):
                for s in msg['sources']:
                    st.caption(f"- {s['source']} (유사도 {s['score']:.2f})")

prompt = st.chat_input('사내 문서에 대해 질문해보세요...')
if prompt:
    st.session_state.rag_history.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('답변 생성 중...'):
            route = rag.route_query(prompt)
            sources, mode_label = [], '📄 문서 검색'

            answer = rag.answer_data_query(prompt, data) if route == 'data' else None
            if answer is not None:
                mode_label = '📊 데이터 조회'
            else:
                result = rag.generate_answer(api_key, prompt)
                answer, sources = result['answer'], result['sources']
                if route == 'data':
                    mode_label = '📄 문서 검색 (데이터 조회 규칙 없음 → 문서 검색으로 대체)'

        st.caption(mode_label)
        st.markdown(answer)
        if sources:
            with st.expander(f'📎 출처 ({len(sources)})'):
                for s in sources:
                    st.caption(f"- {s['source']} (유사도 {s['score']:.2f})")

    st.session_state.rag_history.append({
        'role': 'assistant', 'content': answer, 'sources': sources, 'mode': mode_label,
    })
