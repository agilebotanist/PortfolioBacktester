import streamlit as st
import plotly.express as px
from backtester import random_ticks as random_ticks
from backtester import given_portfolio as given_portfolio
from backtester import SP500_tickers as SP500_tickers

st.set_page_config(page_title="Random portfolio tester", page_icon="📈")

st.title("Buy and Hold : Random portfolio backtester 📈")


startY = st.slider(
    "Enter a **starting** year:",
    min_value=1999,
    value=2017,
    step=1,
    max_value=2024,
    help="2018",
)

nb_years = st.slider(
    "Investment **period** in years:",
    min_value=1,
    value=3,
    max_value=10,
    step=1,
    help="3",
)

_but = st.button("Randomize portfolio")

if ("given_ticks" not in st.session_state) or _but:
    given_ticks = random_ticks(startY, nb_years, 10)
    st.session_state.given_ticks = given_ticks

tickers = st.text_input(
    "Enter a list of **tickers (stocks)** in your portfolio:",
    st.session_state.given_ticks,
    help="APD-CCI-CPRT-ES-INTU-RSG-TT-URI-V-VRSK",
)

# RUN SIMULATION
banch, portfolio, rebalanced = given_portfolio(tickers, startY, nb_years)

# st.write(f"Return on Investment for {nb_years} years:", banch.iloc[-1])

st.write(f"**ROI** for {nb_years} years:", banch["ROI"].iloc[-1])

st.write("ROI with **rebalancing**:", banch["REBALANCED"].iloc[-1])

st.write("**SP500** index perfromance:", banch["SPY"].iloc[-1])

# Create figure
fig_banch = px.line(
    banch,
    title="Banchmark: Portfolio cumulutive gain vs SP500 index",
)

fig_port = px.line(
    portfolio / portfolio.iloc[0],
    title="Portfolio stocks cumulative gain",
)

fig_rebal = px.line(
    rebalanced / rebalanced.iloc[0],
    title="Rebalanced portfolio stocks cumulative gain",
)

# Show figure
st.plotly_chart(fig_banch)

st.plotly_chart(fig_port)

st.plotly_chart(fig_rebal)

available_SP500 = SP500_tickers(startY, nb_years)

st.write(f"**Choose from tickers (stocks) available in our dataset for {startY}:**")
st.write(available_SP500)
