import datetime
import pandas as pd

from load_data import spy_data as spy_data
from load_data import sp500_data as sp500_data


def moment(date, NY, top_n):
    """Calculates momentum scores for stocks based on their performance relative to a benchmark.

    This function identifies top-performing stocks by comparing their returns to the S&P 500 over a specified time period.

    Args:
        date (datetime): The end date for performance calculation.
        NY (int): Number of years to look back for performance analysis.
        top_n (int): Number of top-performing stocks to select.

    Returns:
        pd.DataFrame: A DataFrame containing the top stocks with their:
        - ROI (Return on Investment)
        - ALFA (Abnormal Return relative to benchmark)
        Sorted by ALFA in descending order, limited to top_n stocks.

    Examples:
        >>> end_date = pd.Timestamp('2022-12-31')
        >>> top_momentum_stocks = moment(end_date, NY=1, top_n=10)
    """
    end = date
    start = end - pd.offsets.BDay(252 * NY)

    # Calculate value of initial investment of 10K in the Portfolio
    # initial_investment = 10000, not needed for tests

    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(axis=1, how="all").dropna(thresh=50)  # valid

    # Prepare banchmark set
    spy = spy_data.loc[notnaslice.index[0] : notnaslice.index[-1]]
    spy_score = spy.iloc[-1] / spy.iloc[0]

    # Create DataFrame with tickers as columns and ROI and ALFA as rows
    score = pd.DataFrame(index=["ROI", "ALFA"], columns=sp500_data.columns)
    score.loc["ROI"] = notnaslice.iloc[-1] / notnaslice.iloc[0]
    score.loc["ALFA"] = score.loc["ROI"] - spy_score.values[0]

    calculated_moment = score.loc[:, score.loc["ALFA"] > 0]

    # print(f"calculated_moment: {calculated_moment.head()}")

    # Sort by momentum score and select top_n, including scores
    # Transpose to have tickers as index and ROI, ALFA as columns, then sort and select top_n
    top_tickers_with_scores = (
        calculated_moment.T[["ROI", "ALFA"]]
        .sort_values(by="ALFA", ascending=False)
        .head(top_n)
    )

    return top_tickers_with_scores  # Return top_n tickers


def momentum_portfolio(tickers, start, period):
    """Calculates portfolio performance for selected stocks over a specified time period.

    This function evaluates the performance of a given set of stocks against the S&P 500 benchmark over a defined investment period.

    Args:
        tickers (list): List of stock ticker symbols to include in the portfolio.
        start (datetime): The start date of the investment period.
        period (int): Number of business days to analyze the portfolio performance.

    Returns:
        tuple: A tuple containing three elements:
        - roi (float): Portfolio return as a percentage
        - given_portfolio (pd.DataFrame): Normalized portfolio performance data
        - spy_roi (float): S&P 500 benchmark return for the same period

    Examples:
        >>> start_date = pd.Timestamp('2022-01-01')
        >>> portfolio_tickers = ['AAPL', 'GOOGL', 'MSFT']
        >>> portfolio_roi, portfolio_data, benchmark_roi = momentum_portfolio(portfolio_tickers, start_date, 63)
    """
    end = start + pd.offsets.BDay(period)
    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(axis=1, how="all").dropna(thresh=50)  # valid

    # Prepare banchmark set
    spy = spy_data.loc[notnaslice.index[0] : notnaslice.index[-1]]
    spy_roi = spy.iloc[-1]["SPY"] / spy.iloc[0]["SPY"]

    given_portfolio = notnaslice[tickers].dropna()
    given_portfolio.sort_index(axis=1, inplace=True)

    # cumulative returns  = %difference data to day from the begining of investment
    # SP500 performance in %, since the start day of investment
    given_portfolio = given_portfolio / given_portfolio.iloc[0]
    # calculating cumulative gain from Day 1
    roi = (given_portfolio.sum(axis=1) / given_portfolio.columns.size).iloc[-1]

    return roi, given_portfolio, spy_roi


# Strategy, no commission
def m_strategy(date, n_quarters):
    """Implements a momentum-based investment strategy over multiple quarters.

    This function generates a portfolio strategy by selecting top-performing stocks based on momentum
    and tracking their performance against the S&P 500 over a specified number of quarters.

    Args:
        date (datetime): The starting date for the investment strategy.
        n_quarters (int): Number of quarters to run the momentum strategy.

    Returns:
        pd.DataFrame: A DataFrame containing strategy performance metrics including:
        - Date: Quarterly dates
        - Portfolio: Selected stock tickers
        - ROI: Portfolio return for the quarter
        - SPY: S&P 500 return for the quarter
        - CROI: Cumulative portfolio return
        - CSPY: Cumulative S&P 500 return

    Examples:
        >>> start_date = pd.Timestamp('2020-01-01')
        >>> strategy_results = m_strategy(start_date, 4)
    """

    strategy = pd.DataFrame(columns=["Date", "Portfolio", "ROI", "SPY", "CROI", "CSPY"])

    # Init data in the DataFrame
    strategy = pd.concat(
        [
            strategy,
            pd.DataFrame(
                {
                    "Date": date,
                    "Portfolio": [[""] * 10],
                    "ROI": 1,
                    "SPY": 1,
                    "CROI": 1,
                    "CSPY": 1,
                }
            ),
        ],
        ignore_index=True,
    )

    # Repeat the code 4 times
    for _ in range(n_quarters):

        m = moment(date, 1, 10)

        r, p, s = momentum_portfolio(m.index, date, 63)

        if strategy.empty:
            cr = r
            cs = s
        else:
            cr = r * strategy["CROI"].iloc[-1]
            cs = s * strategy["CSPY"].iloc[-1]

        # update date to the next quarter
        date = date + pd.offsets.BDay(63)

        # Append data to the DataFrame
        strategy = pd.concat(
            [
                strategy,
                pd.DataFrame(
                    {
                        "Date": date,
                        "Portfolio": [m.index.values],
                        "ROI": [r],
                        "SPY": [s],
                        "CROI": [cr],
                        "CSPY": [cs],
                    }
                ),
            ],
            ignore_index=True,
        )

    strategy.set_index("Date", inplace=True)
    strategy.index = pd.to_datetime(strategy.index)
    return strategy


def com_strategy(date, n_quarters, com):
    """Implements a momentum-based investment strategy with transaction cost considerations.

    This function creates an investment strategy that selects top-performing stocks while accounting for transaction costs and portfolio turnover.

    Args:
        date (datetime): The starting date for the investment strategy.
        n_quarters (int): Number of quarters to run the momentum strategy.
        com (float): Transaction cost rate per portfolio rebalancing.

    Returns:
        pd.DataFrame: A DataFrame containing strategy performance metrics including:
        - Date: Quarterly dates
        - Portfolio: Selected stock tickers
        - ROI: Portfolio return for the quarter
        - SPY: S&P 500 return for the quarter
        - COM: Transaction costs
        - CROI: Cumulative portfolio return adjusted for transaction costs
        - CSPY: Cumulative S&P 500 return

    Examples:
        >>> start_date = pd.Timestamp('2020-01-01')
        >>> strategy_results = com_strategy(start_date, 4, 0.01)
    """
    strategy = [
        {
            "Date": date,
            "Portfolio": {"_"},
            "ROI": 1,
            "SPY": 1,
            "COM": com,
            "CROI": 1 - com,
            "CSPY": 1 - com,
        }
    ]
    # Repeat the code 4 times
    for _ in range(n_quarters):

        m = moment(date, 1, 10)

        r, p, s = momentum_portfolio(m.index, date, 63)

        # Access the 'Portfolio' from the last dictionary in the strategy list
        previous_portfolio = strategy[-1]["Portfolio"]
        current_tickers = set(m.index.values)
        remains = previous_portfolio.intersection(current_tickers)
        # Get the number of overlapping elements
        num_remains = len(remains)

        # sell + buy except those remained
        cm = 2 * com * (10 - num_remains) / 10

        if len(strategy) < 2:
            cm = com

        cr = r * strategy[-1]["CROI"] - cm
        cs = s * strategy[-1]["CSPY"]

        # update date to the next quarter
        date = date + pd.offsets.BDay(63)

        strategy.append(
            {
                "Date": date,
                "Portfolio": sorted(set(m.index.values)),
                "ROI": r,
                "SPY": s,
                "COM": cm,
                "CROI": cr,
                "CSPY": cs,
            }
        )

    # final sell of protfolio to cash out
    strategy[-1]["CROI"] = strategy[-1]["CROI"] - com
    strategy[-1]["CSPY"] = strategy[-1]["CSPY"] - com

    # Create the strategy DataFrame
    strategy_df = pd.DataFrame(strategy)
    strategy_df.set_index("Date", inplace=True)
    strategy_df.index = pd.to_datetime(strategy_df.index)

    return strategy_df


def stop_strategy(date, n_quarters, com, loss_rate, restart_nb):
    """Implements a momentum-based investment strategy with a stop-loss mechanism and portfolio recovery rules.

    This function creates an investment strategy that dynamically manages portfolio risk by implementing a stop-loss mechanism and defining conditions for portfolio restart.

    Args:
        date (datetime): The starting date for the investment strategy.
        n_quarters (int): Number of quarters to run the momentum strategy.
        com (float): Transaction cost rate per portfolio rebalancing.
        loss_rate (float): Threshold for portfolio loss that triggers stop-loss mechanism.
        restart_nb (int): Number of consecutive positive quarters required to restart portfolio.

    Returns:
        pd.DataFrame: A DataFrame containing strategy performance metrics including:
        - Date: Quarterly dates
        - Portfolio: Selected stock tickers
        - ROI: Portfolio return for the quarter
        - SPY: S&P 500 return for the quarter
        - COM: Transaction costs
        - CROI: Cumulative portfolio return adjusted for transaction costs
        - CSPY: Cumulative S&P 500 return
        - STOP: Boolean indicating if stop-loss is active
        - N_STOP: Number of consecutive stop-loss periods
        - N_POSITIVE: Number of consecutive positive return periods

    Examples:
        >>> start_date = pd.Timestamp('2020-01-01')
        >>> strategy_results = stop_strategy(start_date, 4, 0.01, 0.1, 2)
    """
    stop = False
    n_positive = 0
    n_stop = 0

    strategy = [
        {
            "Date": date,
            "Portfolio": {"_"},
            "ROI": 1,
            "SPY": 1,
            "COM": com,
            "CROI": 1 - com,
            "CSPY": 1 - com,
            "STOP": stop,
            "N_STOP": n_stop,
            "N_POSITIVE": n_positive,
        }
    ]
    # Repeat the code 4 times
    for _ in range(n_quarters):

        m = moment(date, 1, 10)

        r, p, s = momentum_portfolio(m.index, date, 63)

        portforlio_record = set(m.index.values)

        if r < (1 - loss_rate):
            stop = True
            n_positive = 0
        else:
            n_positive += 1

        if stop:
            n_stop += 1

        if stop and n_stop == 1:  # first stop, sell everything, all the portfolio
            cm = com

        # normal situation, calcualte overlaps in portfolio and calculate commission
        if not stop:
            # Access the 'Portfolio' from the last dictionary in the strategy list
            previous_portfolio = strategy[-1]["Portfolio"]
            current_tickers = portforlio_record
            remains = previous_portfolio.intersection(current_tickers)
            # Get the number of overlapping elements
            num_remains = len(remains)

            # sell + buy except those remained, assume that there are 10 stocks in the portforlio
            cm = 2 * com * (10 - num_remains) / 10

            if len(strategy) < 2:  # fixing recorded numbers for the first round
                cm = com

        # detect restarting situation. Stop happened previously.
        # Sufficient number of positive quarters, buy a portfolio, pay full commission
        if stop and n_positive == restart_nb + 1:
            cm = com
            stop = False
            n_stop = 0

        cr = r * strategy[-1]["CROI"] - cm
        cs = s * strategy[-1]["CSPY"]

        if stop and n_stop > 1:  # noting to sell, just waiting
            cm = 0
            portforlio_record = {"_"}
            cr = strategy[-1]["CROI"]

        # update date to the next quarter
        date = date + pd.offsets.BDay(63)

        strategy.append(
            {
                "Date": date,
                "Portfolio": portforlio_record,
                "ROI": r,
                "SPY": s,
                "COM": cm,
                "CROI": cr,
                "CSPY": cs,
                "STOP": stop,
                "N_STOP": n_stop,
                "N_POSITIVE": n_positive,
            }
        )

    # final sell of protfolio to cash out
    if not stop:
        strategy[-1]["CROI"] = strategy[-1]["CROI"] - com

    strategy[-1]["CSPY"] = strategy[-1]["CSPY"] - com

    # Create the strategy DataFrame
    strategy_df = pd.DataFrame(strategy)
    strategy_df.set_index("Date", inplace=True)
    strategy_df.index = pd.to_datetime(strategy_df.index)

    return strategy_df


def mom_simulate(startY, endY, n_quarters, com, loss_rate, restart_nb):
    """Simulates momentum investment strategies across multiple years with stop-loss mechanism.

    This function runs a momentum-based investment strategy for each year, tracking portfolio performance and comparing it against the S&P 500 benchmark.

    Args:
        startY (int): The starting year for the simulation.
        endY (int): The ending year for the simulation.
        n_quarters (int): Number of quarters to run each strategy.
        com (float): Transaction cost rate per portfolio rebalancing.
        loss_rate (float): Threshold for portfolio loss that triggers stop-loss mechanism.
        restart_nb (int): Number of consecutive positive quarters required to restart portfolio.

    Returns:
        pd.DataFrame: A DataFrame containing performance metrics for each simulated period, including:
        - Year: The year range of the strategy
        - Final_CROI: Cumulative return of the investment strategy
        - Final_CSPY: Cumulative return of the S&P 500 benchmark

    Examples:
        >>> results = mom_simulate(2000, 2022, 4, 0.01, 0.1, 2)
    """
    results = []  # To store the final CROI values

    for year in range(2000, 2023):
        start_date = pd.Timestamp(datetime.datetime(year, 1, 1)).tz_localize("UTC")
        strategy_results = stop_strategy(
            start_date, n_quarters, com, loss_rate, restart_nb
        )  # Assuming com_strategy is your function
        final_croi = strategy_results["CROI"].iloc[-1]  # Get the final CROI value
        final_cspy = strategy_results["CSPY"].iloc[-1]  # Get the final CSPY value
        results.append(
            {
                "Year": f"{year}-{year+n_quarters/4}",
                "Final_CROI": final_croi,
                "Final_CSPY": final_cspy,
            }
        )  # Store the result

    return pd.DataFrame(results)


# DEBUGGING

# 1. Load data
# print(sp500_data.columns)
# print(sp500_data.head())

# 2. Score
# date = pd.Timestamp(datetime.datetime(2024, 12, 1)).tz_localize("UTC")
# print(f"Date: {date}")
# m = moment(date, 1, 10)
# print(f"Momentum: {m}")
# my_tick_list = ", ".join(m.index.tolist())
# print(f"Momentum: {my_tick_list}")

# 3. Momentum portfolio
# date = pd.Timestamp(datetime.datetime(2024, 8, 1)).tz_localize("UTC")
# print(f"Date: {date}")
# m = moment(date, 1, 63)
# r1, p, s1 = momentum_portfolio(m.index, date, 63)
# print(f"ROI 1: {r1}")
# print(f"SPY 1: {s1}")

# 4. Strategy with no commission
# n_quarters = 17
# date = pd.Timestamp(datetime.datetime(2007, 6, 1)).tz_localize("UTC")
# print(f"Date: {date}")
# mystra = m_strategy(date, n_quarters)
# print(mystra)

# 5. Strategy with commission
# n_quarters = 17
# date = pd.Timestamp(datetime.datetime(2007, 6, 1)).tz_localize("UTC")
# print(f"Date: {date}")
# mystra = com_strategy(date, n_quarters, 0.007)
# print(mystra)

# 6. Stop-loss strategy
# n_quarters = 17
# date = pd.Timestamp(datetime.datetime(2007, 6, 1)).tz_localize("UTC")
# print(f"Date: {date}")
# mystra = stop_strategy(date, n_quarters, 0.007, 0.1, 2)
# print(mystra)

# 7. Simulate
# n_quarters = 8
# loss_rate = 0.1
# restart_nb = 1
# com = 0.007
# stats = mom_simulate(2000, 2023, n_quarters, com, loss_rate, restart_nb)
# print(stats)
