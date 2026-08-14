# AACE Mini — 개인화 CRM 캠페인 데모

CSV 고객 데이터 업로드 → 세그먼트 분류 → 세그먼트별 맞춤 메시지 생성까지,
AACE의 핵심 흐름을 축소해 파이썬만으로 만든 데모입니다.

---

## 필요한 것
- Python 3.9 이상
- VS Code (또는 아무 터미널)
- Google Gemini API 키 (무료) — 3단계 메시지 생성에만 필요

---

## 설치 & 실행 (처음 한 번만)

### 1. 파이썬 설치 확인
터미널(VS Code에서 `Ctrl + \`` 로 열기)에 입력:
```
python --version
```
버전이 안 나오면 https://www.python.org/downloads 에서 설치
(설치 시 "Add Python to PATH" 체크 필수)

### 2. 이 폴더로 이동
```
cd 파일이_있는_폴더_경로
```

### 3. 가상환경 만들기 (권장, 안 해도 됨)
```
python -m venv venv
```
- 윈도우: `venv\Scripts\activate`
- 맥/리눅스: `source venv/bin/activate`

### 4. 필요한 패키지 설치
```
pip install -r requirements.txt
```

### 5. 실행
```
streamlit run app.py
```
자동으로 브라우저에 `http://localhost:8501` 이 열립니다.

---

## 사용법
1. **1단계** — "샘플 데이터로 체험"이 켜져 있으면 바로 20명 데이터가 뜹니다.
   내 CSV를 쓰려면 `name, days_since_last_purchase, purchase_count, total_spent`
   컬럼을 맞춰서 올리면 됩니다.
2. **2단계** — 자동으로 VIP / 이탈 위험 / 신규 / 일반 단골로 분류되고 차트가 뜹니다.
3. **3단계** — Gemini API 키를 넣고 "메시지 생성하기"를 누르면
   세그먼트별 맞춤 문구가 생성됩니다.

### Gemini API 키 발급 (무료)
1. https://aistudio.google.com/app/apikey 접속 (구글 로그인)
2. **Create API key** → 키 복사
3. 앱의 3단계 입력칸에 붙여넣기

---

## 다음으로 해볼 만한 확장
- **차트 추가**: 세그먼트별 매출 기여도 파이차트
- **A/B 비교**: 메시지 2개 버전을 만들어 나란히 보여주기
- **배포**: GitHub에 올린 뒤 Streamlit Community Cloud로 무료 공개 URL 만들기
- **진짜 어려운 부분**: 매장마다 다른 실제 데이터 스키마를 자동으로 맞추는 연동
  (← 이게 왜 어려운지 체감하는 게 이 프로젝트의 진짜 목적)
