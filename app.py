"""
AACE Mini - 개인화 CRM 캠페인 데모
CSV 업로드 → 고객 세그먼트 분류 → 세그먼트별 맞춤 메시지 생성

실행: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------------------------------------------------
# 0. 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="AACE Mini", page_icon="🛍️", layout="wide")

st.title("🛍️ AACE Mini — 개인화 CRM 캠페인 데모")
st.caption("고객 데이터를 올리면 → 세그먼트로 나누고 → 세그먼트별 맞춤 메시지를 만들어줍니다.")


# ------------------------------------------------------------
# 1. CSV 업로드
# ------------------------------------------------------------
st.header("1단계 · 고객 데이터 업로드")

uploaded = st.file_uploader("고객 CSV 파일을 올려주세요", type=["csv"])

# 샘플 데이터로 바로 체험할 수 있게
use_sample = st.checkbox("샘플 데이터로 먼저 체험해보기", value=True)

df = None
if uploaded is not None:
    df = pd.read_csv(uploaded)
    use_sample = False
elif use_sample:
    df = pd.read_csv("sample_customers.csv")

if df is None:
    st.info("CSV를 올리거나 '샘플 데이터로 체험'을 켜주세요.")
    st.stop()

st.success(f"고객 {len(df)}명의 데이터를 불러왔습니다.")
st.dataframe(df, use_container_width=True)


# ------------------------------------------------------------
# 2. 세그먼트 분류 (RFM 기반 규칙)
# ------------------------------------------------------------
st.header("2단계 · 고객 세그먼트 분류")

st.markdown(
    "구매 이력을 기준으로 고객을 몇 개의 그룹으로 나눕니다. "
    "여기서는 이해하기 쉬운 **규칙 기반(RFM)** 방식을 씁니다."
)

# 필요한 컬럼: days_since_last_purchase, purchase_count, total_spent
required = {"days_since_last_purchase", "purchase_count", "total_spent"}
if not required.issubset(df.columns):
    st.error(
        "세그먼트 분류에는 다음 컬럼이 필요합니다: "
        + ", ".join(required)
        + "\n샘플 데이터의 컬럼 구조를 참고하세요."
    )
    st.stop()


def assign_segment(row):
    recency = row["days_since_last_purchase"]
    freq = row["purchase_count"]
    spent = row["total_spent"]

    # VIP: 자주, 많이 사고 최근에도 방문
    if spent >= 300000 and freq >= 5 and recency <= 30:
        return "VIP 고객"
    # 이탈 위험: 예전엔 샀는데 오래 안 옴
    if recency >= 90 and freq >= 2:
        return "이탈 위험 고객"
    # 신규: 구매 횟수 적음
    if freq <= 1:
        return "신규 고객"
    # 그 외 일반 단골
    return "일반 단골 고객"


df["세그먼트"] = df.apply(assign_segment, axis=1)

# 세그먼트별 요약
seg_summary = (
    df.groupby("세그먼트")
    .agg(고객수=("세그먼트", "size"), 평균_구매금액=("total_spent", "mean"))
    .reset_index()
    .sort_values("고객수", ascending=False)
)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("세그먼트별 고객 수")
    st.bar_chart(seg_summary.set_index("세그먼트")["고객수"])
with col2:
    st.subheader("세그먼트 요약")
    st.dataframe(seg_summary, use_container_width=True, hide_index=True)

st.subheader("세그먼트가 붙은 고객 목록")
st.dataframe(df, use_container_width=True)


# ------------------------------------------------------------
# 3. 세그먼트별 맞춤 메시지 생성 (Gemini)
# ------------------------------------------------------------
st.header("3단계 · 세그먼트별 맞춤 메시지 생성")

st.markdown(
    "각 세그먼트에 맞는 마케팅 문구를 AI가 만들어줍니다. "
    "Google Gemini의 **무료 API 키**가 필요합니다."
)

with st.expander("🔑 Gemini API 키 발급 방법 (무료)"):
    st.markdown(
        """
        1. https://aistudio.google.com/app/apikey 접속 (구글 계정 로그인)
        2. **Create API key** 클릭 → 키 복사
        3. 아래 입력칸에 붙여넣기 (무료 티어로 충분합니다)
        """
    )

api_key = st.text_input("Gemini API 키", type="password", help="발급받은 키를 붙여넣으세요")

brand = st.text_input("브랜드/매장 이름", value="더마코스")
category = st.text_input("주력 상품 카테고리", value="스킨케어")

# 세그먼트별 메시지 목표(마케팅 의도)를 매핑
segment_goal = {
    "VIP 고객": "감사 인사와 함께 VIP 전용 혜택을 안내해 관계를 강화한다",
    "이탈 위험 고객": "오랜만에 안부를 전하고 재방문을 유도하는 win-back 쿠폰을 제안한다",
    "신규 고객": "첫 구매에 감사하고 제품 사용 팁과 함께 재구매를 부드럽게 유도한다",
    "일반 단골 고객": "꾸준한 방문에 감사하며 교차구매할 만한 신상품을 추천한다",
}


def build_prompt(segment, goal, brand, category):
    return f"""당신은 오프라인 매장 CRM 마케팅 문구 전문가입니다.
아래 조건에 맞는 문자(MMS) 마케팅 메시지를 한국어로 1개 작성하세요.

- 브랜드: {brand}
- 주력 카테고리: {category}
- 고객 세그먼트: {segment}
- 메시지 목표: {goal}

조건:
- 60자 내외로 간결하게
- 자연스럽고 친근한 존댓말
- 맨 앞에 (광고) [{brand}] 표기
- 메시지 본문만 출력 (설명 없이)"""


if st.button("메시지 생성하기", type="primary"):
    if not api_key:
        st.error("먼저 Gemini API 키를 입력해주세요.")
        st.stop()

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        # model = genai.GenerativeModel("gemini-2.0-flash")
        model = genai.GenerativeModel("gemini-flash-latest")

        segments = df["세그먼트"].unique()
        results = []

        progress = st.progress(0, text="메시지 생성 중...")
        for i, seg in enumerate(segments):
            goal = segment_goal.get(seg, "고객에게 맞춤 혜택을 안내한다")
            prompt = build_prompt(seg, goal, brand, category)
            resp = model.generate_content(prompt)
            msg = resp.text.strip()
            count = int((df["세그먼트"] == seg).sum())
            results.append({"세그먼트": seg, "대상 고객 수": count, "생성된 메시지": msg})
            progress.progress((i + 1) / len(segments), text=f"{seg} 완료")

        progress.empty()
        st.success("메시지 생성 완료!")

        result_df = pd.DataFrame(results)
        for _, r in result_df.iterrows():
            st.markdown(f"**{r['세그먼트']}** ({r['대상 고객 수']}명 대상)")
            st.info(r["생성된 메시지"])

        # 다운로드
        csv = result_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "결과 CSV 다운로드", csv, "generated_messages.csv", "text/csv"
        )

    except ImportError:
        st.error(
            "google-generativeai 패키지가 필요합니다. "
            "터미널에서 `pip install google-generativeai` 실행 후 다시 시도하세요."
        )
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")


st.divider()
st.caption(
    "💡 이 데모는 AACE의 핵심 흐름(세그먼트 → 개인화 메시지)을 축소한 것입니다. "
    "실제 제품은 여기에 매장 실데이터 연동, 발송, A/B 실험, 성과 대시보드가 더해집니다."
)
