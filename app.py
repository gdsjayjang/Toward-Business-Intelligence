"""
TBI
"""
import streamlit as st
from src.eda import dist_age
from src.loaders import load_customers

df = load_customers()

st.header('고객 나이 분포')
st.bar_chart(dist_age(df))
