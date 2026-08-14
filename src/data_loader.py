import io
import gdown
import numpy as np
import pandas as pd
import streamlit as st

def data_loader():
    FILE_ID = '1XJzqX42pfUBUWwitvTYkYu8KQQ84tBYY'
    url = f'https://drive.google.com/uc?id={FILE_ID}'
    # path = './data/'
    # data = 'data_clean.parquet'

    # 2. 메모리 버퍼로 다운로드
    output = io.BytesIO()
    gdown.download(url, output, quiet=True)
    output.seek(0)
    
    df = pd.read_parquet(output)
    return df