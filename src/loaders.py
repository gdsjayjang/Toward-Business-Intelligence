import streamlit as st

from src.raw_loader import load_raw_customers
from src.segmentation import assign_segments
from src.message_gen import generate_talking_points

@st.cache_data
def load_customers():
    df = load_raw_customers()
    return assign_segments(df)

@st.cache_data(show_spinner='토킹포인트 생성 중...')
def cached_talking_points(customer_id: str, tags: tuple, _profile, _api_key: str) -> str:
    return generate_talking_points(_profile, tags, _api_key)