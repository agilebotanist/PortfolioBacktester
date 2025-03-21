import streamlit as st
import pandas as pd
import plotly.express as px
from backtester import simulate as simulate

st.set_page_config(page_title="Random Portfolio Strategy Simulator", page_icon="📊")

st.title("Buy and Hold : Random Portfolio Simulator 📊")


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

nb_stocks = st.slider(
    "Nb of **stocks** in portfolio:",
    min_value=1,
    value=10,
    max_value=30,
    step=1,
    help="10",
)

nb_trials = st.slider(
    "Nb of **tests** of random portfolios",
    min_value=1,
    value=50,
    max_value=300,
    step=50,
    help="100",
)

_but = st.button("Run simulation")

if _but:
    stats, med = simulate(startY, nb_years, nb_stocks, nb_trials)

    st.write(
        f"**Median** _Return on Investment_ for {nb_years} years for {nb_trials} random stocks portfolios:",
        med["ROI"],
    )

    st.write("**Median** ROI with rebalancing:", med["REBALANCED"])

    st.write("SP500 index perfromance:", med["SPY"])

    df1 = pd.Series(stats["ROI"]).to_frame()
    df1 = df1.rename(columns={"ROI": "perf"})
    df2 = pd.Series(stats["REBALANCED"]).to_frame()
    df2 = df2.rename(columns={"REBALANCED": "perf"})

    df1["series"] = "HOLD"
    df2["series"] = "REBALANCED"

    df_combined = pd.concat([df1, df2], ignore_index=True)

    # Create figure
    fig_roi = px.histogram(
        df_combined,
        color="series",
        title="ROI histogram",
        # nbins=20,
        text_auto=True,
        opacity=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
        barmode="overlay",
    )
    st.plotly_chart(fig_roi)

    st.write("**Raw data:**", stats)
