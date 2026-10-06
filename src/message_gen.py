# from google import genai

# from src.badge import news_frequency_label
# from configs.genai_config import DEFAULT_GENAI_MODEL

# def generate_talking_points(profile, tags, api_key, model=DEFAULT_GENAI_MODEL):
#     '''세그먼트·RFM·태그 기반 실무자용 응대 토킹포인트를 생성'''
#     news = news_frequency_label(profile['fashion_news_frequency'])
#     tags_text = ', '.join(tags) if tags else '없음'

#     prompt = (
#         "너는 패션 리테일 매장 직원을 돕는 CRM 어시스턴트야.\n"
#         "아래 고객 정보를 바탕으로, 직원이 이 고객을 응대할 때 참고할 토킹포인트를 3~4개 제안해줘.\n\n"
#         "규칙:\n"
#         "- 각 항목은 '무엇을, 왜'가 드러나게 한 문장으로\n"
#         "- 세그먼트와 태그를 근거로 삼을 것\n"
#         "- 번호 매긴 목록으로만 출력하고 서론·맺음말은 쓰지 마\n\n"
#         "[고객 정보]\n"
#         f"- 세그먼트: {profile['segment']}\n"
#         f"- 최근 방문: {profile['days_since_last_purchase']}일 전\n"
#         f"- 총 구매 횟수: {profile['purchase_count']}회\n"
#         f"- 총 구매액: {profile['total_spent']:.2f}\n"
#         f"- 나이: {profile['age']}세\n"
#         f"- 뉴스 수신: {news}\n"
#         f"- 직원 메모 태그: {tags_text}\n"
#     )

#     client = genai.Client(api_key=api_key)
#     response = client.models.generate_content(model=model, contents=prompt)

#     return response.text.strip()


from google import genai
from google.genai import types

from src.badge import news_frequency_label
from src.segments import VIP, CHURN_RISK, LOYAL, NEW, REGULAR
from configs.genai_config import DEFAULT_GENAI_MODEL

# 채널: 지금 매장에 들어온 고객에게 직원이 대면으로 건네는 멘트
HEADER = (
    "너는 패션 리테일 매장의 CRM 어시스턴트야.\n"
    "지금 매장에 방문한 고객에게 직원이 다가가 말을 걸 때 건넬 응대 멘트를 작성해줘.\n"
)

# personalized / baseline 공통 규칙
COMMON_RULES = (
    "- 고객이 지금 매장 안에 있는 상황의 대면 멘트로만 쓸 것"
    " ('연락드렸어요', '편하실 때 들러주세요'처럼 매장 밖 메시지 표현 금지)\n"
    "- 제공되지 않은 정보(구매 상품명, 과거 대화, 이전 방문 때 있었던 일 등)는 절대 지어내지 마."
    " 주어진 정보에 없으면 언급하지 말 것\n"
    "- 존댓말로, 자연스러운 대화체 2~3문장\n"
    "- 공백 포함 100~150자\n"
    "- 응대 문구 본문만 출력하고 따옴표·설명·서론·맺음말은 쓰지 마\n"
)

# 세그먼트별 응대 방향
SEGMENT_GUIDE = {
    VIP:        "최근에도 자주 오는 최우수 고객. 꾸준한 방문에 대한 감사 표현과 신상품·우선 안내 중심. '오랜만' 류 표현 금지",
    LOYAL:      "최근에도 자주 오는 단골 고객. 최근 구매 상품을 근거로 한 취향 기반 추천 중심. '오랜만' 류 표현 금지",
    CHURN_RISK: "예전엔 자주 왔지만 한동안 방문이 끊긴 고객. 다시 찾아준 것에 대한 반가움과 재방문 환영 중심",
    NEW:        "최근 1~3회 구매를 시작한 지 얼마 안 된 고객. 다시 찾아준 것에 대한 반가움, 브랜드 소개와 지난 구매가 만족스러웠는지 확인 중심. '오랜만' 류 표현 금지",
    REGULAR:    "가끔 구매하는 기존 고객. 다시 찾아준 것에 대한 인사와 부담 없이 둘러보도록 관심 유도 중심. '어려운 발걸음' 같은 과한 표현 금지",
}


def generate_talking_points(profile, tags, api_key,
                              model=DEFAULT_GENAI_MODEL,
                              personalized=False, temperature=0.7):
    '''직원이 매장 방문 고객에게 건넬 맞춤 응대 멘트를 생성.
    personalized=False면 고객 정보 없이 생성(평가용 baseline).'''

    if personalized:
        news = news_frequency_label(profile['fashion_news_frequency'])
        tags_text = ', '.join(tags) if tags else '없음'
        recent_items = profile.get('recent_items') or []
        items_text = ', '.join(recent_items) if recent_items else '정보 없음'
        guide = SEGMENT_GUIDE.get(profile['segment'], SEGMENT_GUIDE[REGULAR])
        prompt = (
            HEADER
            + "아래 고객 정보를 바탕으로 이 고객에게 맞춘 멘트로 써줘.\n\n"
            + "규칙:\n"
            + COMMON_RULES
            + "- 이 고객은 이미 구매 이력이 있는 기존 고객이야. '처음이시죠', '처음 방문' 등 첫 방문으로 대하는 표현 금지\n"
            + f"- 응대 방향: {guide}\n"
            + "- 최근 구매 상품 유형이 있으면 그중 하나를 한국어로 자연스럽게 바꿔 반드시 언급하고, 응대 방향에 맞게 연결할 것"
            " (예: Trousers → 바지). 목록에 없는 상품은 지어내지 말 것. '정보 없음'이면 특정 상품을 언급하지 마\n"
            + "- 직원 메모 태그가 있으면 반영할 것\n"
            + "- 세그먼트 이름(VIP, 이탈위험 등)과 구매액·구매 횟수·방문 일수 같은 내부 수치는 문구에 직접 쓰지 마\n\n"
            + "[고객 정보]\n"
            + f"- 세그먼트: {profile['segment']}\n"
            + f"- 최근 방문: {profile['days_since_last_purchase']}일 전\n"
            + f"- 총 구매 횟수: {profile['purchase_count']}회\n"
            + f"- 총 구매액: {profile['total_spent']:.2f}\n"
            + f"- 나이: {profile['age']}세\n"
            + f"- 뉴스 수신: {news}\n"
            + f"- 최근 구매 상품 유형: {items_text}\n"
            + f"- 직원 메모 태그: {tags_text}\n"
        )
    else:
        prompt = (
            HEADER
            + "\n규칙:\n"
            + COMMON_RULES
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return response.text.strip()