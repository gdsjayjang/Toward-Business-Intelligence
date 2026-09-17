import itertools
from pathlib import Path

import numpy as np
import streamlit as st
from google import genai

from configs.genai_config import DEFAULT_GENAI_MODEL, DEFAULT_EMBEDDING_MODEL

CORPUS_DIR = Path('docs/rag_corpus')
MAX_CHUNK_CHARS = 700
OVERLAP_CHARS = 80
TOP_K = 4
MIN_SIMILARITY = 0.35

GROUNDED_ANSWER_PROMPT = '''너는 BI 조직의 사내 문서 기반 QA 어시스턴트야.
아래 [참고 문서]에 주어진 내용에 근거해서만 답변해.
문서에 근거가 없으면 추측하지 말고 "문서에서 근거를 찾지 못했습니다."라고만 답해.
답변은 간결한 한국어로 작성하고, 필요하면 목록으로 정리해.

[참고 문서]
{context}

[질문]
{query}
'''

DATA_INTENT_KEYWORDS = [
    '총 고객', '고객 수', '평균 구매', '총 구매', '매출',
    '세그먼트별 고객', '세그먼트 분포', '몇 명',
]


def load_corpus_files():
    '''docs/rag_corpus 내 마크다운 문서를 (파일명, 본문) 목록으로 로드'''
    return [
        (path.name, path.read_text(encoding='utf-8'))
        for path in sorted(CORPUS_DIR.glob('*.md'))
    ]


def chunk_document(filename, text, max_chars=MAX_CHUNK_CHARS, overlap_chars=OVERLAP_CHARS):
    '''문단 단위로 묶어 300~500토큰(한국어 기준 약 500~700자) 근사 청크로 분할'''
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    chunks, buf = [], ''
    for p in paragraphs:
        candidate = f'{buf}\n\n{p}'.strip() if buf else p
        if len(candidate) > max_chars and buf:
            chunks.append(buf)
            tail = buf[-overlap_chars:]
            buf = f'{tail}\n\n{p}'.strip()
        else:
            buf = candidate

        while len(buf) > max_chars * 1.5:
            chunks.append(buf[:max_chars])
            buf = buf[max_chars:]

    if buf:
        chunks.append(buf)

    return [{'source': filename, 'chunk_id': i, 'text': c} for i, c in enumerate(chunks)]


def build_corpus_chunks():
    chunks = []
    for filename, text in load_corpus_files():
        chunks.extend(chunk_document(filename, text))
    return chunks


def _corpus_fingerprint():
    '''문서가 수정되면 캐시가 자동 무효화되도록 mtime 기반 지문 생성'''
    parts = [f'{p.name}:{p.stat().st_mtime}' for p in sorted(CORPUS_DIR.glob('*.md'))]
    return '|'.join(parts)


def _embed(client, texts, task_type, title=None, model=DEFAULT_EMBEDDING_MODEL):
    config = {'task_type': task_type}
    if title:
        config['title'] = title
    response = client.models.embed_content(model=model, contents=texts, config=config)
    return [e.values for e in response.embeddings]


@st.cache_resource(show_spinner='📚 문서 인덱싱 중...')
def build_index(api_key, fingerprint):
    '''코퍼스를 청크→임베딩하여 (청크 목록, 임베딩 행렬)로 캐싱'''
    chunks = build_corpus_chunks()
    client = genai.Client(api_key=api_key)

    vectors = []
    for source, group in itertools.groupby(chunks, key=lambda c: c['source']):
        texts = [c['text'] for c in group]
        vectors.extend(_embed(client, texts, task_type='RETRIEVAL_DOCUMENT', title=source))

    embeddings = np.array(vectors, dtype=np.float32)
    return {'chunks': chunks, 'embeddings': embeddings}


def _cosine_top_k(query_vec, doc_matrix, k):
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    doc_norms = doc_matrix / (np.linalg.norm(doc_matrix, axis=1, keepdims=True) + 1e-8)
    sims = doc_norms @ query_norm
    idx = np.argsort(-sims)[:k]
    return idx, sims[idx]


def retrieve(api_key, query, top_k=TOP_K, min_similarity=MIN_SIMILARITY):
    index = build_index(api_key, _corpus_fingerprint())
    client = genai.Client(api_key=api_key)
    query_vec = np.array(_embed(client, [query], task_type='RETRIEVAL_QUERY')[0], dtype=np.float32)

    idx, sims = _cosine_top_k(query_vec, index['embeddings'], top_k)
    return [
        {**index['chunks'][i], 'score': float(s)}
        for i, s in zip(idx, sims) if s >= min_similarity
    ]


def _format_context(chunks):
    return '\n\n---\n\n'.join(
        f"(출처: {c['source']} #{c['chunk_id']})\n{c['text']}" for c in chunks
    )


def _dedupe_sources(chunks):
    best = {}
    for c in chunks:
        if c['source'] not in best or c['score'] > best[c['source']]:
            best[c['source']] = c['score']
    return [{'source': k, 'score': v} for k, v in sorted(best.items(), key=lambda x: -x[1])]


def generate_answer(api_key, query, top_k=TOP_K, model=DEFAULT_GENAI_MODEL):
    '''RAG 파이프라인: 검색 → grounding 프롬프트 → 생성. 근거 없으면 모른다고 답함'''
    chunks = retrieve(api_key, query, top_k=top_k)
    if not chunks:
        return {'answer': '문서에서 근거를 찾지 못했습니다.', 'sources': []}

    prompt = GROUNDED_ANSWER_PROMPT.format(context=_format_context(chunks), query=query)
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    answer = response.text.strip()

    # 유사도 임계값을 넘겨 검색은 됐지만 모델이 grounding 실패로 판단한 경우,
    # 관련 없는 출처를 답변에 달지 않는다.
    if answer.startswith('문서에서 근거를 찾지 못했습니다'):
        return {'answer': answer, 'sources': []}

    return {'answer': answer, 'sources': _dedupe_sources(chunks)}


def route_query(query):
    '''문서 질문 vs 정형 데이터 질문을 가르는 최소한의 라우터'''
    return 'data' if any(k in query for k in DATA_INTENT_KEYWORDS) else 'doc'


def answer_data_query(query, data):
    '''라우터가 데이터 의도로 판단한 질문 중 정해진 패턴만 대시보드 집계로 직접 응답.
    해당하는 패턴이 없으면 None을 반환해 RAG 경로로 폴백한다.'''
    from src import analytics

    kpis = analytics.overall_kpis(data)

    if '세그먼트' in query and ('분포' in query or '고객 수' in query):
        dist = analytics.segment_distribution(data)
        lines = [f"- {row.segment}: {row.count:,}명 ({row.pct * 100:.1f}%)" for row in dist.itertuples()]
        return '세그먼트별 고객 분포:\n' + '\n'.join(lines)
    if '총 고객' in query or ('고객 수' in query and '세그먼트' not in query):
        return f"전체 고객 수는 {kpis['total_customers']:,}명입니다."
    if '평균 구매' in query:
        return f"평균 구매금액은 ${kpis['avg_monetary']:,.2f}입니다."
    if '총 구매' in query or '매출' in query:
        return f"총 구매금액은 ${kpis['total_monetary']:,.2f}입니다."

    return None
