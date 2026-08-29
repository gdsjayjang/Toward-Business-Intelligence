import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def dist_age(df):

    return df['age'].value_counts().sort_index()