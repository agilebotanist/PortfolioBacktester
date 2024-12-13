import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

from momentum import stop_strategy
from momentum import com_strategy

st.set_page_config(page_title="Momentum Portfolio", page_icon="📈")

st.title("Momentum : Portfolio backtester 📈")


date_input = st.date_input(
    "Enter a **starting** date:",
    min_value=datetime.date(2000, 1, 1),
    value=datetime.date(2008, 2, 1),
    max_value=datetime.date(2024, 12, 1),
    help="2007/1/1",
)

n_quarters = st.slider(
    "Investment **period** in quarters:",
    min_value=1,
    value=4,
    max_value=24,
    step=1,
    help="4",
)

com = st.number_input(
    label="Transaction cost rate per portfolio rebalancing",
    step=0.01,
    format="%.4f",
    value=0.007,
)
st.write("Transaction commission", com)

loss_rate = st.number_input(
    label="Threshold for portfolio loss that triggers stop-loss mechanism",
    step=0.05,
    value=0.1,
    format="%.2f",
)
st.write("Stop-loss threshold", loss_rate)

restart_nb = st.number_input(
    label="Number of consecutive positive quarters required to restart portfolio",
    value=2,
    step=1,
)
st.write(f"Restart after {restart_nb} positive quarters.")


date = pd.Timestamp(date_input).tz_localize("UTC")
stopstra = stop_strategy(date, n_quarters, com, loss_rate, restart_nb)

# Create the plot using plotly.express
fig_stop = px.line(
    stopstra,
    x=stopstra.index,
    y=["CROI", "CSPY"],
    title="STOP-LOSS: Cumulative ROI vs Cumulative SPY Return",
)

# Show figure
st.plotly_chart(fig_stop)

st.write(
    "**Momentum-based investment strategy with a stop-loss mechanism and portfolio recovery rules:**"
)
st.write(stopstra)

comstra = com_strategy(date, n_quarters, com)

# Create the plot using plotly.express
fig_com = px.line(
    comstra,
    x=comstra.index,
    y=["CROI", "CSPY"],
    title="MOMENTUM: Cumulative ROI vs Cumulative SPY Return",
)

# Show figure
st.plotly_chart(fig_com)

st.write("**Momentum-based investment strategy with transaction cost considerations:**")
st.write(comstra)
