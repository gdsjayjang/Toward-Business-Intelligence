import numpy as np
import pandas as pd
import streamlit as st

def data_loader():
    path = './data/'
    data = 'data_clean.parquet'
    
    return pd.read_parquet(path + data)