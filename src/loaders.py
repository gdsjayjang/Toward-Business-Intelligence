import streamlit as st

from src.data_loader import data_loader

@st.cache_data
def load_customers():
    return data_loader()