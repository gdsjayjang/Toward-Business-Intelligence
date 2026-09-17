# 🏠 Toward Business Intelligence

패션 리테일 고객 거래 데이터를 RFM 기준으로 세그먼트화하고, 이를 실무자가 바로 쓸 수 있는 BI 대시보드와 생성형 AI 도구로 제공하는 Streamlit 프로젝트

## 프로젝트 목적

- 원천 거래 로그를 고객 단위 RFM(Recency·Frequency·Monetary) 지표로 집계하고 규칙 기반으로 세그먼트를 부여해, "우리 고객이 어떻게 나뉘는가"를 대시보드로 보여준다.
- 생성형 AI(Google Gemini)를 실제 BI 실무 워크플로우 세 지점에 접목한다.
  1. 매장 직원이 남긴 메모 → 구조화 태그 자동 추출
  2. 고객 세그먼트·RFM·태그 → 응대 토킹포인트 자동 생성
  3. 세그먼트 정의·지표 정의·데이터 사전 등 **사내 문서**를 RAG로 인덱싱해, 질문에 근거 문서와 출처를 달아 답하는 QA 어시스턴트

## 주요 기능

| 페이지 | 파일 | 설명 |
|---|---|---|
| 🏠 홈 | [app.py](app.py) | 페이지 안내, 세그먼트 소개, 연령대별 고객 분포 |
| 🧑‍💼 고객 응대 | [pages/customer_service.py](pages/customer_service.py) | 고객 ID 검색 → RFM 프로필 조회 → 메모를 AI 태그로 변환 → AI 응대 토킹포인트 생성 |
| 📊 경영진 대시보드 | [pages/executive_bi.py](pages/executive_bi.py) | 전체 KPI(고객 수·평균/총 구매금액), 세그먼트별 분포·비중, 세그먼트별 RFM 원값 평균 |
| 🤖 BI 어시스턴트 (RAG) | [pages/bi_assistant.py](pages/bi_assistant.py) | 사내 문서 기반 QA 챗봇. 답변마다 근거 문서 출처를 표시하고, 정형 데이터 질문은 자동으로 데이터 조회로 라우팅 |

## RFM 세그먼트 로직

`src/segmentation.py`에서 R/F/M 세 축을 4분위 점수(1~4)로 나눈 뒤 규칙으로 세그먼트를 배정합니다.

| 세그먼트 | 조건 | 설명 |
|---|---|---|
| VIP | R=4, F=4, M=4 | R·F·M 모두 최상위 |
| 이탈위험 | (F≥3 또는 M≥3) 이고 R≤2 | 과거엔 우량했지만 최근 방문이 뜸함 |
| 충성 | R≥3, F≥3, M≥3 (VIP 제외) | 최근에도 자주·많이 구매 |
| 신규 | R≥3, F≤1 | 최근 유입, 구매 이력 적음 |
| 일반 | 위 조건 미해당 | 나머지 |

세그먼트 정의와 지표 계산식은 [docs/rag_corpus/](docs/rag_corpus/)에도 문서화되어 있으며, BI 어시스턴트가 이 문서를 근거로 답합니다.

## RAG 파이프라인 (BI 어시스턴트)

`src/rag.py`에 구현된 6단계 파이프라인입니다.

1. **코퍼스**: [docs/rag_corpus/](docs/rag_corpus/)의 마크다운 문서 7개 (세그먼트 정의, 지표 정의, 데이터 사전, 세그먼트별 전략, 과거 리포트 요약, AI 기능 안내, FAQ)
2. **청킹**: 문단 단위로 묶어 약 500~700자(한국어 기준 300~500토큰 근사) 청크로 분할
3. **임베딩**: Gemini 임베딩 모델(`gemini-embedding-001`)로 벡터화. 문서는 `RETRIEVAL_DOCUMENT`, 질의는 `RETRIEVAL_QUERY` task_type을 구분해 사용
4. **벡터 저장/검색**: 별도 벡터 DB 없이 numpy 배열 + 코사인 유사도로 top-k 청크 검색 (`st.cache_resource`로 인덱스 캐싱, 문서 수정 시 자동 재인덱싱)
5. **생성**: 검색된 청크 + 질문을 Gemini(`gemini-3.5-flash-lite`)에 전달하며 "주어진 문서에 근거해서만 답하고, 없으면 모른다고 답하라"를 프롬프트에 명시 — 이 부분이 grounding
6. **UI**: 답변 아래 "출처" expander로 근거 문서 파일명과 유사도 점수를 표시

**라우터(스트레치)**: 질문에 `평균 구매`, `세그먼트 분포` 등 정형 데이터 키워드가 있으면 RAG를 거치지 않고 대시보드 집계 함수(`src/analytics.py`)로 직접 답합니다(`route_query`/`answer_data_query`). 정형 데이터 질의를 RAG로 억지로 처리하지 않기 위한 최소한의 분기입니다.

## 기술 스택

- **UI**: Streamlit (멀티페이지 앱)
- **데이터 처리**: pandas, numpy
- **생성형 AI**: Google Gemini (`google-genai` SDK) — 텍스트 생성 + 임베딩
- **시각화**: Streamlit 내장 차트, matplotlib

## 프로젝트 구조

```
app.py                      # 홈 페이지
pages/
  customer_service.py       # 고객 응대 페이지
  executive_bi.py           # 경영진 대시보드 페이지
  bi_assistant.py           # BI 어시스턴트(RAG) 페이지
src/
  raw_loader.py             # 집계된 parquet 로드
  loaders.py                # 캐싱된 데이터/AI 결과 로더 (st.cache_data)
  segmentation.py           # RFM 4분위 점수화 + 세그먼트 규칙
  segments.py                # 세그먼트 이름/색상 상수
  analytics.py               # KPI, 세그먼트 분포, RFM 요약 집계
  customer_profile.py        # 고객 ID → 프로필 dict 변환
  badge.py                   # 상태값 → 색상 뱃지 매핑
  tagging.py                  # 메모 → 태그 (Gemini)
  message_gen.py              # 세그먼트/태그 → 토킹포인트 (Gemini)
  rag.py                       # RAG 파이프라인(청킹·임베딩·검색·생성) + 데이터 질문 라우터
  genai_config.py              # 사용 모델명 상수
  eda.py                        # 간단 EDA 유틸(연령 분포)
docs/rag_corpus/                # BI 어시스턴트가 참조하는 사내 문서 코퍼스
data/
  customers_dashboard.parquet   # 고객 단위 집계 데이터(앱이 실제로 사용)
  sample_customers.csv          # 샘플 데이터
utils/customers_dashboard.py    # 원천 거래 로그 → 고객 단위 RFM 집계 오프라인 스크립트
notebooks/                      # 초기 프로토타입(AACE Mini) — 세그먼트→메시지 생성 미니 데모, 본 앱과 별도
configs/, models/                # 향후 확장을 위한 자리(현재 비어있는 스텁)
```

## 실행 방법

```bash
git clone <repo-url>
cd Toward-Business-Intelligence
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

`.streamlit/secrets.toml`에 Gemini API 키를 등록합니다 (해당 파일은 git에 커밋되지 않습니다).

```toml
GENAI_API_KEY = "여기에_발급받은_키"
```

```bash
streamlit run app.py
```

## 데이터 파이프라인

- `utils/customers_dashboard.py`: 원천 거래 로그(`t_dat`, `price` 등 트랜잭션 단위, 저장소에는 미포함)를 `customer_id` 기준으로 그룹화해 R/F/M 원값을 계산하고 `data/customers_dashboard.parquet`로 저장하는 **오프라인** 전처리 스크립트입니다. 앱 실행 시 매번 돌리는 것이 아니라 사전에 한 번 생성해둔 결과물을 앱이 읽습니다.
- 앱은 이 스냅샷 parquet 파일만 읽으므로, 특정 기간(예: "지난달 매출") 단위 집계는 현재 지원하지 않습니다.

## 한계 및 다음 단계

- RAG 코퍼스는 포트폴리오 시연용으로 직접 작성한 문서 7개(총 20페이지 이내)이며, 실제 사내 문서 규모로 확장하는 것은 범위 밖입니다.
- 정식 LTV/CLV 모델은 없고 누적 구매금액(`total_spent`)을 근사치로 사용합니다.
- 라우터는 파인튜닝이나 멀티 에이전트 없이 키워드 기반 if 분기로 최소 구현했습니다. 실제 서비스라면 의도 분류를 더 정교하게 다듬어야 합니다.

## 배포

`.devcontainer/`를 포함하고 있어 GitHub Codespaces에서 바로 실행 가능하며, Streamlit Community Cloud로도 배포되어 있습니다.
