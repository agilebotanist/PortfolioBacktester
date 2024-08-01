import streamlit as st
from load_data import download_sp500 as download_sp500
from load_data import spy_data as spy_data
from load_data import sp500_data as sp500_data

st.set_page_config(page_title="Update Data", page_icon="🔄")

st.title("Update stocks data 🔄")

st.write("Download the latest SP500 data from Yahoo Finance.")

_but = st.button("Update data")

if _but:
    with st.spinner('Wait for it...'):
        spy_data, sp500_data = download_sp500()
    st.success("Done!")
