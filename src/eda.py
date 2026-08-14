import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def drop_customer_id(df):
    '''
    customer_id 중복 제거 후 df 반환
    '''
    return df.drop_duplicates(subset='customer_id')

def dist_age(df):
    new_df = drop_customer_id(df)

    return new_df['age'].value_counts().sort_index()