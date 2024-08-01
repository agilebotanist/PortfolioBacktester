import datetime
import random
import pandas as pd
from load_data import spy_data as spy_data
from load_data import sp500_data as sp500_data


def random_portfolio(startY, nb_years, nb_tickers):
    # init dates
    start = datetime.datetime(startY, 1, 1)
    end = datetime.datetime(startY + nb_years, 1, 1)

    # Calculate value of initial investment of 10K in the Portfolio
    # initial_investment = 10000, not needed for tests

    # Prepare banchmark set
    spy = spy_data.loc[start:end]

    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(
        axis=1
    )  # is that valid? or a bias, since dropping some values
    # that do not exist for the whole period

    # Randomly select NB (e.g. 20) tickers for portfolio
    random_portfolio = notnaslice.sample(n=nb_tickers, axis="columns")
    random_portfolio.sort_index(axis=1, inplace=True)

    # cumulative returns  = %difference data to day from the begining of investment
    banch = (
        spy / spy.iloc[0]
    )  # SP500 performance in %, since the start day of investment

    cumulative = (
        random_portfolio / random_portfolio.iloc[0]
    )  # calculating cumulative gain from Day 1
    banch["ROI"] = (
        cumulative.sum(axis=1) / cumulative.columns.size
    )  # Summing all partfolio tickers performance and normalizing, since we want to compare with single SPY gains.

    banch["REBALANCED"], rebalanced_portfolio = rebalance(
        random_portfolio, 252
    )  # another sample, rebalanacing afer 252 days

    # record stats for various tests

    # tick = "-".join(random_portfolio.columns)

    # print(tick)

    return banch, random_portfolio, rebalanced_portfolio


def rebalance(portfolio, period):
    nperiods = round(portfolio.index.size / period, 0)  # rounding up or down :/
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


banch, portfolio, rebalanced_portfolio = random_portfolio(2018, 3, 10)
# print(banch.tail())


def given_portfolio(tickers, startY, nb_years):
    # init dates
    start = datetime.datetime(startY, 1, 1)
    end = datetime.datetime(startY + nb_years, 1, 1)

    # Calculate value of initial investment of 10K in the Portfolio
    # initial_investment = 10000, not needed for tests

    # Prepare banchmark set
    spy = spy_data.loc[start:end]

    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(
        axis=1
    )  # is that valid? or a bias, since dropping some values
    # that do not exist for the whole period

    ticker_names = tickers.split("-")

    # Randomly select NB (e.g. 20) tickers for portfolio
    given_portfolio = notnaslice[ticker_names]
    given_portfolio.sort_index(axis=1, inplace=True)

    # cumulative returns  = %difference data to day from the begining of investment
    banch = (
        spy / spy.iloc[0]
    )  # SP500 performance in %, since the start day of investment

    cumulative = (
        given_portfolio / given_portfolio.iloc[0]
    )  # calculating cumulative gain from Day 1
    banch["ROI"] = (
        cumulative.sum(axis=1) / cumulative.columns.size
    )  # Summing all partfolio tickers performance and normalizing, since we want to compare with single SPY gains.

    banch["REBALANCED"], rebalanced_portfolio = rebalance(
        given_portfolio, 252
    )  # another sample, rebalanacing afer 252 days

    # record stats for various tests

    return banch, given_portfolio, rebalanced_portfolio


def SP500_tickers(startY, nb_years):
    # init dates
    start = datetime.datetime(startY, 1, 1)
    end = datetime.datetime(startY + nb_years, 1, 1)
    # Slice stocks data
    timeslice = sp500_data.loc[start:end]
    notnaslice = timeslice.dropna(axis=1)

    all_ticks = sorted(list(notnaslice.columns))

    return "-".join(all_ticks)


def random_ticks(startY, nb_years, nb_stocks):
    sp_ticks = SP500_tickers(startY, nb_years).split("-")
    rand_ticks = random.sample(sp_ticks, nb_stocks)
    return "-".join(sorted(rand_ticks))


def simulate(startY, nb_years, nb_stocks, nb_trials):
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
            "ROI1Y",
            "SPY1Y",
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
                "ROI1Y": banch["ROI"].iloc[252],  # portfolio perf after 1Y
                "SPY1Y": banch["SPY"].iloc[252],  # SP500 perf after 1Y
                "ROI": banch["ROI"].iloc[-1],  # portfolio perf
                "REBALANCED": banch["REBALANCED"].iloc[-1],  # rebalanced portfolio perf
                "SPY": banch["SPY"].iloc[-1],  # SP500 perf after 3Y
            },
            ignore_index=True,
        )
    med = stats[["ROI1Y", "SPY1Y", "ROI", "REBALANCED", "SPY"]].median()
    return stats, med


# stats, med = simulate(2017, 3, 10, 10)

# print(med)
# print(stats.head())
# print(stats.size)
# print(stats.tail())

# b, gp, rp = given_portfolio("AFL-AJG-AME-AXP", 2018, 3)

# print(gp.head())

# print(sp500_data.columns)

# given_ticks = "APD-CCI-CPRT-ES-INTU-RSG-TT-URI-V-VRSK"
# rand_ticks = random.sample(list(sp500_data.columns), 20)
# given_ticks = "-".join(sorted(rand_ticks))

# print(given_ticks)
