from google import genai

from src.badge import news_frequency_label
from src.genai_config import DEFAULT_GENAI_MODEL

def generate_talking_points(profile, tags, api_key, model=DEFAULT_GENAI_MODEL):
    '''세그먼트·RFM·태그 기반 실무자용 응대 토킹포인트를 생성'''
    news = news_frequency_label(profile['fashion_news_frequency'])
    tags_text = ', '.join(tags) if tags else '없음'

    prompt = (
        "너는 패션 리테일 매장 직원을 돕는 CRM 어시스턴트야.\n"
        "아래 고객 정보를 바탕으로, 직원이 이 고객을 응대할 때 참고할 토킹포인트를 3~4개 제안해줘.\n\n"
        "규칙:\n"
        "- 각 항목은 '무엇을, 왜'가 드러나게 한 문장으로\n"
        "- 세그먼트와 태그를 근거로 삼을 것\n"
        "- 번호 매긴 목록으로만 출력하고 서론·맺음말은 쓰지 마\n\n"
        "[고객 정보]\n"
        f"- 세그먼트: {profile['segment']}\n"
        f"- 최근 방문: {profile['days_since_last_purchase']}일 전\n"
        f"- 총 구매 횟수: {profile['purchase_count']}회\n"
        f"- 총 구매액: {profile['total_spent']:.2f}\n"
        f"- 나이: {profile['age']}세\n"
        f"- 뉴스 수신: {news}\n"
        f"- 직원 메모 태그: {tags_text}\n"
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)

    return response.text.strip()