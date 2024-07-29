import streamlit as st
import plotly.express as px
import backtester


st.title("Buy and Hold : Portfolio backtester")

startY = st.number_input(
    "Enter a starting year:", min_value=1999, max_value=2021, help="2018"
)

nb_years = st.number_input(
    "Enter a number of years:", min_value=1, max_value=10, help="3"
)

nb_tickers = st.number_input(
    "Enter a number of tickers (stocks):", min_value=1, max_value=30, help="20"
)

banch, portfolio, rebalanced = backtester.random_portfolio(
    startY, nb_years, nb_tickers
)

tick = "-".join(portfolio.columns)

st.write(f"**{nb_tickers} random SP500 stocks:**", tick)

st.write(f"Return on Investment for {nb_years} years:", banch.tail())

# Create figure
fig_banch = px.line(
    banch,
    title="Banchmark",
)

fig_port = px.line(
    portfolio/portfolio.iloc[0],
    title="Portfolio",
)

fig_rebal = px.line(
    rebalanced/rebalanced.iloc[0],
    title="Rebalanced portfolio",
)

# Show figure
st.plotly_chart(fig_banch)

st.plotly_chart(fig_port)

st.plotly_chart(fig_rebal)
