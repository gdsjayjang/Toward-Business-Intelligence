"""
AACE Mini - 개인화 CRM 캠페인 데모
CSV 업로드 → 고객 세그먼트 분류 → 세그먼트별 맞춤 메시지 생성

실행: streamlit run app.py
"""
import pandas as pd
import streamlit as st
from src.eda import dist_age
from src.data_loader import data_loader

# DATA LOAD
cached_loader = st.cache_data(data_loader)
df = cached_loader()

print(df.head(5))
print('LOAD OK')

st.header('고객 나이 분포')
st.bar_chart(dist_age(df))
