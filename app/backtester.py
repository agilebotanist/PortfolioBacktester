import datetime
from load_data import safe_load

spy_data, sp500_data = safe_load()


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

    tick = "-".join(random_portfolio.columns)

    print(tick)

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
print(banch.tail())


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


# b, gp, rp = given_portfolio("AFL-AJG-AME-AXP", 2018, 3)

# print(gp.head())

# print(sp500_data.columns)

# given_ticks = "APD-CCI-CPRT-ES-INTU-RSG-TT-URI-V-VRSK"
# rand_ticks = random.sample(list(sp500_data.columns), 20)
# given_ticks = "-".join(sorted(rand_ticks))

# print(given_ticks)
