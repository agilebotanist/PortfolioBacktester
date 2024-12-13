import datetime
import random
import pandas as pd
from load_data import spy_data as spy_data
from load_data import sp500_data as sp500_data


def random_portfolio(startY, nb_years, nb_tickers):
    """Generates a random portfolio of stocks for backtesting investment strategies.

    This function creates a portfolio by randomly selecting a specified number of stock tickers from a given time period.

    Args:
        startY (int): The starting year for stock selection.
        nb_years (int): Number of years to consider for stock selection.
        nb_tickers (int): Number of stock tickers to include in the portfolio.

    Returns:
        pd.DataFrame: A portfolio performance DataFrame with selected random stocks.

    Examples:
        >>> random_portfolio_results = random_portfolio(2010, 5, 10)
    """
    return given_portfolio(random_ticks(startY, nb_years, nb_tickers), startY, nb_years)


def rebalance(portfolio, period):
    """Rebalances a portfolio at specified intervals.

    This function redistributes portfolio weights at regular intervals to maintain a consistent investment strategy.

    Args:
        portfolio (pd.DataFrame): The input portfolio performance data.
        period (int): Number of periods between portfolio rebalancing.

    Returns:
        pd.DataFrame: A rebalanced portfolio with adjusted weights.

    Notes:
        - Calculates the number of rebalancing periods based on total portfolio size
        - Helps maintain consistent portfolio allocation over time

    Examples:
        >>> rebalanced_portfolio = rebalance(original_portfolio, 63)
    """
    # rounding up or down :/
    nperiods = round(portfolio.index.size / period, 0)

    n = 0
    cumul = portfolio / portfolio.iloc[0]
    cumul = cumul / cumul.columns.size
    sum = cumul.sum(axis=1)
    while n < nperiods:
        gain = sum.iloc[n * period]  # portfolio total at period
        reinvest = round(
            gain / cumul.columns.size, 6
        )  # balancing, deviding total among all possitions
        # re-starting cumulating from new reinvestment till the end
        cumul[n * period :] = (
            reinvest * portfolio[n * period :] / portfolio.iloc[n * period]
        )
        sum[n * period :] = cumul[n * period :].sum(axis=1)
        n += 1
    return sum, cumul


def given_portfolio(tickers, startY, nb_years):
    """Generates and analyzes a portfolio performance for specified stock tickers.

    This function creates a portfolio from selected stock tickers, calculates cumulative returns, and compares performance against the S&P 500 benchmark.

    Args:
        tickers (str): Hyphen-separated list of stock ticker symbols.
        startY (int): The starting year for portfolio analysis.
        nb_years (int): Number of years to analyze portfolio performance.

    Returns:
        tuple: A tuple containing three elements:
        - banch (pd.DataFrame): Performance metrics including benchmark comparison
        - given_portfolio (pd.DataFrame): Raw portfolio stock prices
        - rebalanced_portfolio (pd.DataFrame): Portfolio with periodic rebalancing

    Notes:
        - Filters out stocks with insufficient data
        - Calculates cumulative returns
        - Performs portfolio rebalancing at yearly intervals

    Examples:
        >>> performance, raw_data, rebalanced = given_portfolio('AAPL-GOOGL-MSFT', 2010, 5)
    """
    # init dates
    start = pd.Timestamp(datetime.datetime(startY, 1, 1))
    start = start.tz_localize("UTC")
    end = pd.Timestamp(datetime.datetime(startY + nb_years, 1, 1))
    end = end.tz_localize("UTC")

    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(axis=1, how="all").dropna(thresh=50)
    # is that valid? or a bias, since dropping some values
    # that do not exist for the whole period

    # Prepare banchmark set
    spy = spy_data.loc[notnaslice.index[0] : notnaslice.index[-1]]

    ticker_names = tickers.split("-")

    given_portfolio = notnaslice[ticker_names].dropna()
    given_portfolio.sort_index(axis=1, inplace=True)

    # cumulative returns  = %difference data to day from the begining of investment
    banch = (
        spy / spy.iloc[0]
    )  # SP500 performance in %, since the start day of investment

    cumulative = given_portfolio / given_portfolio.iloc[0]
    # calculating cumulative gain from Day 1

    banch["ROI"] = cumulative.sum(axis=1) / cumulative.columns.size
    # Summing all partfolio tickers performance and normalizing, since we want to compare with single SPY gains.

    banch["REBALANCED"], rebalanced_portfolio = rebalance(
        given_portfolio, 252
    )  # another sample, rebalanacing afer 252 days

    # record stats for various tests

    banch = banch.dropna()

    return banch, given_portfolio, rebalanced_portfolio


def SP500_tickers(startY, nb_years):
    """Retrieves a list of valid S&P 500 stock tickers for a specified time period.

    This function filters and returns stock tickers that have sufficient data within the given date range.

    Args:
        startY (int): The starting year for ticker selection.
        nb_years (int): Number of years to consider for ticker availability.

    Returns:
        str: A hyphen-separated string of stock ticker symbols sorted alphabetically.

    Notes:
        - Filters out stocks with insufficient data
        - Requires at least 50 non-null data points
        - Returns tickers sorted alphabetically

    Examples:
        >>> tickers = SP500_tickers(2010, 5)
    """
    # init dates
    start = pd.Timestamp(datetime.datetime(startY, 1, 1))
    start = start.tz_localize("UTC")
    end = pd.Timestamp(datetime.datetime(startY + nb_years, 1, 1))
    end = end.tz_localize("UTC")
    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(axis=1, how="all").dropna(thresh=50)

    all_ticks = sorted(list(notnaslice.columns))

    return "-".join(all_ticks)


def random_ticks(startY, nb_years, nb_stocks):
    """Generates a random subset of stock tickers from the S&P 500 for a specified time period.

    This function selects a specified number of unique stock tickers from available S&P 500 stocks within a given date range.

    Args:
        startY (int): The starting year for stock selection.
        nb_years (int): Number of years to consider for stock availability.
        nb_stocks (int): Number of stock tickers to randomly select.

    Returns:
        str: A hyphen-separated string of randomly selected stock ticker symbols, sorted alphabetically.

    Notes:
        - Uses SP500_tickers to get available stocks
        - Randomly samples from available tickers
        - Returns tickers sorted alphabetically

    Examples:
        >>> random_tickers = random_ticks(2010, 5, 10)
    """
    sp_ticks = SP500_tickers(startY, nb_years).split("-")
    rand_ticks = random.sample(sp_ticks, nb_stocks)
    return "-".join(sorted(rand_ticks))


def simulate(startY, nb_years, nb_stocks, nb_trials):
    """Conducts a Monte Carlo simulation of portfolio performance using random stock selections.

    This function generates multiple random portfolios to analyze investment strategy performance and compare against benchmark returns.

    Args:
        startY (int): The starting year for portfolio simulation.
        nb_years (int): Number of years to simulate portfolio performance.
        nb_stocks (int): Number of stocks to include in each random portfolio.
        nb_trials (int): Number of random portfolio simulations to run.

    Returns:
        pd.DataFrame: A DataFrame containing performance statistics for simulated portfolios, including:
        - TICKERS: Selected stock ticker symbols
        - START: Starting year
        - NYEARS: Number of years simulated
        - ROI: Portfolio return
        - REBALANCED: Rebalanced portfolio performance
        - SPY: S&P 500 benchmark performance
        - RBDAYS: Rebalancing interval

    Notes:
        - Uses random stock selection for each trial
        - Calculates portfolio performance with and without rebalancing
        - Compares portfolio performance to S&P 500 benchmark

    Examples:
        >>> simulation_results = simulate(2010, 5, 10, 100)
    """
    # init stats
    stats = pd.DataFrame(
        columns=[
            "TICKERS",
            "START",
            "NYEARS",
            "ROI",
            "REBALANCED",
            "SPY",
            "RBDAYS",
            # "ROI1Y",
            # "SPY1Y",
        ]
    )

    for _ in range(nb_trials):
        rand = random_ticks(startY, nb_years, nb_stocks)
        banch, portfolio, rebalanced_portfolio = given_portfolio(rand, startY, nb_years)
        stats = stats._append(
            {
                "TICKERS": rand,
                "START": startY,
                "NYEARS": nb_years,
                "RBDAYS": 252,
                # "ROI1Y": banch["ROI"].iloc[252],  # portfolio perf after 1Y
                # "SPY1Y": banch["SPY"].iloc[252],  # SP500 perf after 1Y
                "ROI": banch["ROI"].iloc[-1],  # portfolio perf
                "REBALANCED": banch["REBALANCED"].iloc[-1],  # rebalanced portfolio perf
                "SPY": banch["SPY"].iloc[-1],  # SP500 perf after 3Y
            },
            ignore_index=True,
        )
    med = stats[
        [
            # "ROI1Y", "SPY1Y",
            "ROI",
            "REBALANCED",
            "SPY",
        ]
    ].median()
    return stats, med


# DEBUGGING

# 1. Load data

# print(sp500_data.columns)
# print(sp500_data.head())

# 2. Random portfolio

# banch, p, rp = random_portfolio(2018, 3, 10)
# print(banch.tail())
# print(p.tail())

# 3. Given portfolio

# banch, p, rp = given_portfolio("SAN.PA", 2017, 3)
# print(banch.head())
# print(p.head())
# print(rp.head())


# 4. SP500 tickers

# t = SP500_tickers(2018, 5)
# print(t)

# 5. Random tickers

# t = random_ticks(2018, 3, 10)
# print(t)

# 6. Simulation

# stats, med = simulate(2017, 3, 10, 10)
# print(med)
# print(stats.head())
# print(stats.size)
# print(stats.tail())
