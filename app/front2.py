import streamlit as st
import random
import datetime
import plotly.express as px
import backtester


st.title("Buy and Hold : Portfolio backtester. v2")


startY = st.slider(
    "Enter a starting year:", min_value=1999, value=2017, step=1,
    max_value=2023, help="2018"
)

nb_years = st.slider(
    "Enter a number of years:", min_value=1, value=3, max_value=10,
    step=1, help="3"
)


start = datetime.datetime(startY, 1, 1)
end = datetime.datetime(startY + nb_years, 1, 1)


# Slice stocks data
timeslice = backtester.sp500_data.loc[start:end]
notnaslice = timeslice.dropna(axis=1)

all_ticks = sorted(list(notnaslice.columns))

_but = st.button("Randomize portfolio")

if ("given_ticks" not in st.session_state) or _but:
    rand_ticks = random.sample(all_ticks, 10)
    given_ticks = "-".join(sorted(rand_ticks))
    st.session_state.given_ticks = given_ticks

tickers = st.text_input(
    "Enter a list of tickers (stock) in your portfolio:",
    st.session_state.given_ticks,
    help="APD-CCI-CPRT-ES-INTU-RSG-TT-URI-V-VRSK",
)

# RUN SIMULATION
banch, portfolio, rebalanced = backtester.given_portfolio(tickers, startY,
                                                          nb_years)

st.write(f"Return on Investment for {nb_years} years:", banch.iloc[-1])

# Create figure
fig_banch = px.line(
    banch,
    title="Banchmark",
)

fig_port = px.line(
    portfolio / portfolio.iloc[0],
    title="Portfolio",
)

fig_rebal = px.line(
    rebalanced / rebalanced.iloc[0],
    title="Rebalanced portfolio",
)

# Show figure
st.plotly_chart(fig_banch)

st.plotly_chart(fig_port)

st.plotly_chart(fig_rebal)

available_SP500 = "-".join(all_ticks)

st.write(f"**Choose from SP500 tickers (stocks) available in {startY}:**")
st.write(available_SP500)
