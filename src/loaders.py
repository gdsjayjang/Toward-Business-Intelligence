import streamlit as st

from src.data_loader import data_loader
from src.segmentation import assign_segments

@st.cache_data
def load_customers():
    df = data_loader()

    return assign_segments(df)