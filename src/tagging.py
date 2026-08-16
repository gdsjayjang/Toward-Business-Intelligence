import json
from google import genai

def memo2tags(memo, api_key, model='gemini-flash-latest'):
    if not memo or not memo.strip(): return []

    client = genai.Client(api_key=api_key)
    prompt = (
        "다음은 매장 직원이 고객 응대 후 남긴 메모야.\n"
        "여기서 재사용 가능한 구조화 태그를 추출해줘.\n\n"
        "규칙:\n"
        "- 'key:value' 형식 또는 단일 키워드, 모두 소문자 영문\n"
        "- 최대 5개\n"
        "- JSON 배열만 출력하고 다른 설명은 절대 하지 마\n"
        '- 예시: ["promo-responsive", "fit:slim", "size-sensitive"]\n\n'
        f"메모: {memo}"
    )

    response = client.models.generate_content(model=model, contents=prompt)

    # 쓸데없는 수식 제거
    text = response.text.strip()
    text = text.replace('```json', '').replace('```', '').strip()

    try:
        tags = json.loads(text)
        return [t for t in tags if isinstance(t, str)][:5]
    except json.JSONDecodeError:
        return []