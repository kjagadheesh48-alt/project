import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower().str.strip()
    return df