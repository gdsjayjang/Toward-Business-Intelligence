"""
TBI
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

st.header('고객 나이 분포vh')
st.bar_chart(dist_age(df))
