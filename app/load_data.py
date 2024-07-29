import yfinance as yf
import pandas as pd
import datetime
import os


def download_sp500():
    # Read and print the stock tickers that make up S&P500
    sp500_info = pd.read_html(
        'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    print(sp500_info.head())

    sp500_tickers = sp500_info.Symbol.to_list()

    print(sp500_tickers)

    history = datetime.datetime(1999, 1, 1)

    sp500_data = yf.download(sp500_tickers, history, auto_adjust=True)['Close']
    spy_data = yf.download('SPY', history, auto_adjust=True)['Close']

    sp500_data.to_csv('./sp500_1999.csv', date_format='%Y-%m-%d')
    spy_data.to_csv('./spy_1999.csv', date_format='%Y-%m-%d')

    return spy_data, sp500_data


def restore_sp500():
    spy_data = pd.read_csv('./spy_1999.csv')
    spy_data.set_index("Date", inplace=True)
    spy_data.index = pd.to_datetime(spy_data.index)
    spy_data.rename(columns={'Close': 'SPY'}, inplace=True)

    sp500_data = pd.read_csv('./sp500_1999.csv')
    sp500_data.set_index("Date", inplace=True)
    sp500_data.index = pd.to_datetime(sp500_data.index)

    return spy_data, sp500_data


def safe_load():
    fp1 = './spy_1999.csv'
    fp2 = './sp500_1999.csv'
    if (os.path.exists(fp1) and os.path.exists(fp2)):
        return restore_sp500()
    else:
        return download_sp500()


spy_data, sp500_data = safe_load()

print(sp500_data.head())
