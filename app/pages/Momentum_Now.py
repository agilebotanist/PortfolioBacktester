import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

from momentum import stop_strategy
from momentum import com_strategy

st.set_page_config(page_title="Momentum Now", page_icon="📈")

st.title("Momentum : Checking backwards 📈")


date_input = st.date_input(
    "Enter a **starting** date:",
    min_value=datetime.date(2000, 1, 1),
    value="today",
    max_value="today",
    help="2007/1/1",
)

n_quarters = st.slider(
    "Looking back **period** in quarters:",
    min_value=1,
    value=2,
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


date = pd.Timestamp(date_input).tz_localize("UTC") - pd.offsets.BDay(n_quarters * 63)

comstra = com_strategy(date, n_quarters, com)

# Create the plot using plotly.express
fig_com = px.line(
    comstra,
    x=comstra.index,
    y=["ROI", "SPY"],
    title="MOMENTUM: ROI vs SPY Return for a given quarter",
)

# Show figure
st.plotly_chart(fig_com)

st.write("**Momentum-based investment strategy with transaction cost considerations:**")
st.write(comstra)
