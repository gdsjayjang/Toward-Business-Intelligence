# H&M Personalized Fashion Recommendations

## 1. 개요

- 출처: [Kaggle - H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
- 내용: H&M 고객의 약 2년치(2018-09 ~ 2020-09) 구매 이력, 고객 메타데이터, 상품 메타데이터

| 파일 | 설명 | 키 |
|---|---|---|
| `transactions_train.csv` | 구매 거래 로그 | `customer_id`, `article_id` |
| `customers.csv` | 고객 메타데이터 | `customer_id` |
| `articles.csv` | 상품 메타데이터 | `article_id` |

```
customers.csv ──(customer_id)──┐
                               ├── transactions_train.csv
articles.csv  ──(article_id)───┘
```

---

## 2. 데이터셋

### 2.1 transactions_train.csv

**2018-09-20 ~ 2020-09-22** 동안 구매한 내역.\
각 row는 **"어떤 날짜에, 어떤 고객이, 어떤 상품을, 얼마에, 어느 채널에서 샀는가"** 를 의미.

- 영수증(주문) 단위가 아니라 **고객 × 상품 × 날짜** 단위로 기록됨.
- 수량 컬럼은 없다. 같은 날 같은 고객이 같은 상품을 여러 개 사면 **동일한 row가 반복**됨. 즉, 중복되는 row는 구매 수량을 의미.

#### 데이터 형태

| 항목 | 값 |
|---|---|
| 파일 크기 | 약 3.2GB |
| 행 수 | 31,788,324 |
| 열 수 | 5 |
| 기간 | 2018-09-20 ~ 2020-09-22 |

#### 컬럼 명세

| 컬럼 | 타입(권장) | 설명 |
|---|---|---|
| `t_dat` | datetime | 구매 날짜 |
| `customer_id` | str | 고객 ID (64자리 해시). `customers.csv`와 연결 |
| `article_id` | str | 상품 ID. `articles.csv`와 연결 |
| `price` | float32 | 구매 가격 |
| `sales_channel_id` | int8 | 판매 채널(1, 2). 공식 정의는 없음, 보통 1=매장, 2=온라인으로 해석 |

#### 샘플

| | t_dat | customer_id | article_id | price | sales_channel_id |
|---|---|---|---|---|---|
| 0 | 2018-09-20 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | 663713001 | 0.050831 | 2 |
| 1 | 2018-09-20 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | 541518023 | 0.030492 | 2 |
| 2 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 505221004 | 0.015237 | 2 |
| 3 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 685687003 | 0.016932 | 2 |
| 4 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 685687004 | 0.016932 | 2 |


### 2.2 customers.csv
고객 1명당 1 row인 **고객 메타데이터**.\
각 row는 **고객이 몇 살이고, 어떤 멤버십 상태이며, 패션 뉴스를 얼마나 받아보는가"** 를 의미.

- `customer_id` 기준으로 `transactions_train.csv`와 연결됨.
- 구매 이력이 없는 고객도 포함되어 있음. 즉, `customers.csv`의 고객 수 ≥ 거래 로그에 등장하는 고객 수.
- `FN`, `Active`는 0/1이 아니라 **1 또는 결측(NaN)** 으로 기록됨. 결측은 "해당 없음"으로 해석.

#### 데이터 형태

| 항목 | 값 |
|---|---|
| 메모리 사용량 | 256.7MB |
| 행 수 | 1,371,980 |
| 열 수 | 7 |

#### 컬럼 명세

| 컬럼 | 타입(권장) | 설명 | 결측 |
|---|---|---|---|
| `customer_id` | str | 고객 ID (64자리 해시). `transactions_train.csv`와 연결 | 0 |
| `FN` | float32 | Fashion News 구독 여부. 1 또는 NaN | 895,050 (65.2%) |
| `Active` | float32 | 커뮤니케이션 활성 여부. 1 또는 NaN. 공식 정의는 없음 | 907,576 (66.2%) |
| `club_member_status` | category | 멤버십 상태. `ACTIVE`, `PRE-CREATE`, `LEFT CLUB` | 6,062 (0.4%) |
| `fashion_news_frequency` | category | 패션 뉴스 수신 빈도. `NONE`, `Regularly`, `Monthly` 등 | 16,011 (1.2%) |
| `age` | float32 | 나이. 16 ~ 99세, 평균 36.4세, 중앙값 32세 | 15,861 (1.2%) |
| `postal_code` | str | 우편번호 (해시) | 0 |

#### 샘플

| | customer_id | FN | Active | club_member_status | fashion_news_frequency | age | postal_code |
|---|---|---|---|---|---|---|---|
| 0 | 00000dbacae5abe5e23885899a1fa44253a17956c6d1c3... | NaN | NaN | ACTIVE | NONE | 49.0 | 52043ee2162cf5aa7ee79974281641c6f11a68d276429a... |
| 1 | 0000423b00ade91418cceaf3b26c6af3dd342b51fd051e... | NaN | NaN | ACTIVE | NONE | 25.0 | 2973abc54daa8a5f8ccfe9362140c63247c5eee03f1d93... |
| 2 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | NaN | NaN | ACTIVE | NONE | 24.0 | 64f17e6a330a85798e4998f62d0930d14db8db1c054af6... |
| 3 | 00005ca1c9ed5f5146b52ac8639a40ca9d57aeff4d1bd2... | NaN | NaN | ACTIVE | NONE | 54.0 | 5d36574f52495e81f019b680c843c443bd343d5ca5b1c2... |
| 4 | 00006413d8573cd20ed7128e53b7b13819fe5cfc2d801f... | 1.0 | 1.0 | ACTIVE | Regularly | 52.0 | 25fa5ddee9aac01b35208d01736e57942317d756b32ddd... |

### 2.3 articles.csv

상품 1개(색상·변형 단위)당 1 row인 **상품 메타데이터**.\
각 row는 **"이 상품이 어떤 제품이고, 어떤 종류·색상·부서에 속하는가"** 를 의미.

- `article_id` 기준으로 `transactions_train.csv`와 연결됨.
- `article_id` = `product_code` + 3자리 변형 번호. 즉, `product_code`는 같은 제품, `article_id`는 그 제품의 색상·변형 단위.
  - 예: `article_id` 108775015 → `product_code` 108775
- 대부분의 속성이 **코드(`_no`, `_code`, `_id`)와 이름(`_name`) 쌍**으로 구성됨. 분석 시 둘 중 하나만 사용.
- 일부 코드 컬럼에 **-1** 값이 존재(`product_type_no`, `graphical_appearance_no`, `colour_group_code`, `perceived_colour_*`). 미분류 값으로 추정.

#### 데이터 형태

| 항목 | 값 |
|---|---|
| 메모리 사용량 | 47.7MB |
| 행 수 | 105,542 |
| 열 수 | 25 |

#### 컬럼 명세

| 구분 | 코드 컬럼 | 이름 컬럼 | 설명 |
|---|---|---|---|
| 식별자 | `article_id` | - | 상품 ID. `transactions_train.csv`와 연결 |
| 제품 | `product_code` | `prod_name` | 제품 코드 / 제품명 |
| 제품 유형 | `product_type_no` | `product_type_name` | 세부 유형 (예: Vest top, Bra) |
| 제품 그룹 | - | `product_group_name` | 상위 유형 그룹 (예: Garment Upper body, Underwear) |
| 외관 | `graphical_appearance_no` | `graphical_appearance_name` | 패턴·무늬 (예: Solid, Stripe) |
| 색상 | `colour_group_code` | `colour_group_name` | 세부 색상 (예: Black, White, Off White) |
| 색상 명도 | `perceived_colour_value_id` | `perceived_colour_value_name` | 밝기 계열 |
| 색상 계열 | `perceived_colour_master_id` | `perceived_colour_master_name` | 대표 색상 계열 |
| 부서 | `department_no` | `department_name` | 담당 부서 (예: Jersey Basic, Clean Lingerie) |
| 인덱스 | `index_code` | `index_name` | 상품 라인 (예: A=Ladieswear, B=Lingeries/Tights) |
| 인덱스 그룹 | `index_group_no` | `index_group_name` | 상위 라인 (예: 1=Ladieswear) |
| 섹션 | `section_no` | `section_name` | 매장 섹션 (예: Womens Everyday Basics) |
| 의류 그룹 | `garment_group_no` | `garment_group_name` | 의류 분류 (예: Jersey Basic, Under-, Nightwear) |
| 설명 | - | `detail_desc` | 상품 상세 설명(텍스트). 결측 416건 (0.4%) |


#### 샘플

주요 컬럼

| | article_id | product_code | prod_name | product_type_name | product_group_name | graphical_appearance_name | colour_group_name | index_group_name | section_name | detail_desc |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 108775015 | 108775 | Strap top | Vest top | Garment Upper body | Solid | Black | Ladieswear | Womens Everyday Basics | Jersey top with narrow shoulder straps. |
| 1 | 108775044 | 108775 | Strap top | Vest top | Garment Upper body | Solid | White | Ladieswear | Womens Everyday Basics | Jersey top with narrow shoulder straps. |
| 2 | 108775051 | 108775 | Strap top (1) | Vest top | Garment Upper body | Stripe | Off White | Ladieswear | Womens Everyday Basics | Jersey top with narrow shoulder straps. |
| 3 | 110065001 | 110065 | OP T-shirt (Idro) | Bra | Underwear | Solid | Black | Ladieswear | Womens Lingerie | Microfibre T-shirt bra with underwired, moulde... |
| 4 | 110065002 | 110065 | OP T-shirt (Idro) | Bra | Underwear | Solid | White | Ladieswear | Womens Lingerie | Microfibre T-shirt bra with underwired, moulde... |

- 0~2행은 같은 `product_code`(108775)의 색상·패턴 변형. `article_id` 뒤 3자리만 다름.


### 2.4 merged_df (data_clean.parquet)

`transactions_train.csv`에 `customers.csv`의 고객 속성을 붙인 **거래 단위 통합 데이터**.\
각 row는 **"어떤 날짜에, 어떤 고객이, 어떤 상품을, 얼마에, 어느 채널에서 샀는가 + 그 고객은 누구인가"** 를 의미.

- 거래 1건당 1 row. 행 수는 `transactions_train.csv`와 동일(31,788,324).
- `customers.csv`의 나머지 9,699명은 구매 이력이 없어 포함되지 않음.

#### 생성 과정

```
customers.csv  ── 전처리 ──┐
                           ├── merge(on='customer_id', how='inner') → merged_df.csv → merged_df.parquet
transactions_train.csv ────┘
```

| 단계 | 내용 |
|---|---|
| customers 전처리 | `postal_code` 삭제 |
| | `age`: 결측 → **-1**로 채움 |
| | `FN`, `Active`: 결측 → False, 1 → True (bool) |
| transactions 전처리 | `t_dat` → datetime 변환 |
| 병합 | `customer_id` 기준 inner join. 거래 고객이 모두 customers에 있어 left join과 결과 동일 |
| 저장 | `merged_df.csv` 저장 → `read_csv` → `to_parquet`로 `merged_df.parquet` 생성 |

#### 데이터 형태

| 항목 | 값 |
|---|---|
| 메모리 사용량 | 4.5GB |
| 행 수 | 31,788,324 |
| 열 수 | 10 |
| 기간 | 2018-09-20 ~ 2020-09-22 |

#### 컬럼 명세

| 컬럼 | 타입(실제) | 출처 | 설명 |
|---|---|---|---|
| `t_dat` | str | transactions | 구매 날짜. 문자열 상태라 날짜 연산 시 `pd.to_datetime` 필요 |
| `customer_id` | str | transactions | 고객 ID (64자리 해시) |
| `article_id` | int64 | transactions | 상품 ID. `articles.csv`와 연결 |
| `price` | float64 | transactions | 구매 가격 |
| `sales_channel_id` | int64 | transactions | 판매 채널(1, 2). 보통 1=매장, 2=온라인으로 해석 |
| `FN` | bool | customers | Fashion News 구독 여부 |
| `Active` | bool | customers | 커뮤니케이션 활성 여부 |
| `club_member_status` | str | customers | 멤버십 상태(`ACTIVE`, `PRE-CREATE`, `LEFT CLUB`). 결측 있음 |
| `fashion_news_frequency` | str | customers | 패션 뉴스 수신 빈도(`NONE`, `Regularly`, `Monthly`). 결측 있음 |
| `age` | int64 | customers | 나이. **-1 = 결측** |

#### 샘플

| | t_dat | customer_id | article_id | price | sales_channel_id | FN | Active | club_member_status | fashion_news_frequency | age |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2018-09-20 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | 663713001 | 0.050831 | 2 | False | False | ACTIVE | NONE | 24 |
| 1 | 2018-09-20 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | 541518023 | 0.030492 | 2 | False | False | ACTIVE | NONE | 24 |
| 2 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 505221004 | 0.015237 | 2 | True | True | ACTIVE | Regularly | 32 |
| 3 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 685687003 | 0.016932 | 2 | True | True | ACTIVE | Regularly | 32 |
| 4 | 2018-09-20 | 00007d2de826758b65a93dd24ce629ed66842531df6699... | 685687004 | 0.016932 | 2 | True | True | ACTIVE | Regularly | 32 |


## 3. 대시보드 데이터

### 3.1 customers_dashboard.parquet

`merged_df.parquet`(거래 단위)를 `customer_id`로 집계한 **고객 단위 요약 테이블**. 대시보드가 실제로 읽는 파일.\
각 row는 **"이 고객은 누구이고, 언제 마지막으로 샀고, 몇 개를 샀고, 얼마를 썼는가"** 를 의미.

- 고객 1명당 1 row. 3,179만 행 → 136만 행으로 축소되어 Streamlit Cloud에서 로딩 가능.
- 구매 이력이 있는 고객만 포함(1,362,281명). 구매 이력 없는 9,699명은 제외.
- RFM 세그먼트(VIP, 충성 등)는 이 파일에 저장하지 않음. 앱 로딩 시 `src/segmentation.py`에서 계산 → 규칙을 바꿔도 파일 재생성 불필요.

#### 생성 과정

```
data/data_clean.parquet (거래 단위, 31,788,324행)
  └─ groupby('customer_id').agg(...)
       └─ days_since_last_purchase 계산
            └─ data/customers_dashboard.parquet (고객 단위, 1,362,281행)
```

| 결과 컬럼 | 계산 | 비고 |
|---|---|---|
| `age`, `club_member_status`, `fashion_news_frequency` | `first` | 고객 속성은 모든 거래 row에서 동일하므로 대표값 1개 |
| `last_purchase` | `t_dat`의 `max` | 마지막 구매일 |
| `purchase_count` | `t_dat`의 `count` | **F (Frequency)** |
| `total_spent` | `price`의 `sum` | **M (Monetary)** |
| `days_since_last_purchase` | `ref_date - last_purchase` | **R (Recency)**. 일 단위 |

- `ref_date` = 데이터 내 가장 최근 거래일(**2020-09-22**). 2020년 스냅샷이므로 오늘 날짜가 아닌 데이터 종료일 기준.

#### 데이터 형태

| 항목 | 값 |
|---|---|
| 행 수 | 1,362,281 |
| 열 수 | 8 |
| 기준일 (`ref_date`) | 2020-09-22 |

#### 컬럼 명세

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `customer_id` | str | 고객 ID (64자리 해시) |
| `age` | int64 | 나이. **-1 = 결측** |
| `club_member_status` | str | 멤버십 상태(`ACTIVE`, `PRE-CREATE`, `LEFT CLUB`). 결측 있음 |
| `fashion_news_frequency` | str | 패션 뉴스 수신 빈도(`NONE`, `Regularly`, `Monthly`). 결측 있음 |
| `last_purchase` | datetime | 마지막 구매일 |
| `purchase_count` | int64 | 구매 상품 개수 (F) |
| `total_spent` | float64 | 총 구매액 (M). 스케일링된 값 |
| `days_since_last_purchase` | int64 | 마지막 구매 후 경과일 (R). 작을수록 최근 |

#### 샘플

| | customer_id | age | club_member_status | fashion_news_frequency | last_purchase | purchase_count | total_spent | days_since_last_purchase |
|---|---|---|---|---|---|---|---|---|
| 0 | 00000dbacae5abe5e23885899a1fa44253a17956c6d1c3... | 49 | ACTIVE | NONE | 2020-09-05 | 21 | 0.648983 | 17 |
| 1 | 0000423b00ade91418cceaf3b26c6af3dd342b51fd051e... | 25 | ACTIVE | NONE | 2020-07-08 | 86 | 2.601932 | 76 |
| 2 | 000058a12d5b43e67d225668fa1f8d618c13dc232df0ca... | 24 | ACTIVE | NONE | 2020-09-15 | 18 | 0.704780 | 7 |
| 3 | 00005ca1c9ed5f5146b52ac8639a40ca9d57aeff4d1bd2... | 54 | ACTIVE | NONE | 2019-06-09 | 2 | 0.060983 | 471 |
| 4 | 00006413d8573cd20ed7128e53b7b13819fe5cfc2d801f... | 52 | ACTIVE | Regularly | 2020-08-12 | 13 | 0.469695 | 41 |

#### 주의사항

- **`purchase_count`는 방문 횟수가 아니라 구매 상품 개수.** 같은 날 5개를 사면 5로 집계됨. 방문 횟수가 필요하면 `('t_dat', 'nunique')`.
- **`age = -1`은 결측.** 연령 차트·평균 계산 시 `age >= 0`으로 필터링.
- **`total_spent`는 스케일링된 값.** 실제 금액이 아니므로 고객 간 상대 비교용.
- `FN`, `Active`, `sales_channel_id`는 집계에서 제외됨. 채널 선호 등 분석 시 집계 항목에 추가 필요.