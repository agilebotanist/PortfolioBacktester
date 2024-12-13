import yfinance as yf
import pandas as pd
import datetime
import os
import sys


def download_sp500():
    """Downloads and saves historical stock price data for S&P 500 companies.

    This function retrieves stock price information for S&P 500 companies from Wikipedia and Yahoo Finance, and saves the data to CSV files.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
        - spy_data: Historical closing prices for the SPY ETF
        - sp500_data: Historical closing prices for S&P 500 constituent stocks

    Notes:
        - Automatically downloads data from 1999-01-01 onwards
        - Saves downloaded data to 'spy_1999.csv' and 'sp500_1999.csv'
        - Excludes specific tickers like 'BRK.B' and 'BF.B'
        - Adds some additional tickers not in the original S&P 500 list

    Examples:
        >>> spy, sp500 = download_sp500()
    """
    # Read and print the stock tickers that make up S&P500
    sp500_info = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )[0]
    # print(sp500_info.head())

    # convert and add missing ['CROX', 'SKX', 'SHOO', 'AER']
    sp500_tickers = sp500_info.Symbol.to_list() + [
        "CROX",
        "SKX",
        "SHOO",
        "AER",
        "SAN.PA",
    ]

    # print(sp500_tickers)

    history = datetime.datetime(1999, 1, 1)

    sp500_data = yf.download(sp500_tickers, history, auto_adjust=True)["Close"]
    spy_data = yf.download("SPY", history, auto_adjust=True)["Close"]

    # clean up
    sp500_data = sp500_data.drop(["BRK.B", "BF.B"], axis=1)

    sp500_data.to_csv("./sp500_1999.csv", date_format="%Y-%m-%d")
    spy_data.to_csv("./spy_1999.csv", date_format="%Y-%m-%d")

    return spy_data, sp500_data


def restore_sp500():
    """Loads and preprocesses historical S&P 500 stock price data from CSV files.

    This function reads previously saved stock price data for the SPY ETF and S&P 500 constituents, preparing them for further analysis.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
        - spy_data: Processed SPY ETF closing prices with datetime index
        - sp500_data: Processed S&P 500 constituent stock prices with datetime index

    Notes:
        - Assumes CSV files 'spy_1999.csv' and 'sp500_1999.csv' exist in the current directory
        - Converts index to datetime
        - Renames columns for consistency

    Examples:
        >>> spy, sp500 = restore_sp500()
    """
    spy_data = pd.read_csv("./spy_1999.csv")
    spy_data.set_index("Date", inplace=True)
    spy_data.index = pd.to_datetime(spy_data.index)
    spy_data.rename(columns={"Close": "SPY"}, inplace=True)

    sp500_data = pd.read_csv("./sp500_1999.csv")
    sp500_data.set_index("Date", inplace=True)
    sp500_data.index = pd.to_datetime(sp500_data.index)

    # Make spy_data and sp500_data timezone-aware
    spy_data.index = spy_data.index.tz_localize("UTC")
    sp500_data.index = sp500_data.index.tz_localize("UTC")

    return spy_data, sp500_data


def safe_load():
    """Safely loads historical stock price data, downloading if necessary.

    This function checks for existing CSV files and either restores previously saved data or downloads fresh stock price information.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
        - spy_data: SPY ETF closing prices
        - sp500_data: S&P 500 constituent stock prices

    Notes:
        - Checks for 'spy_1999.csv' and 'sp500_1999.csv' in the current directory
        - Calls restore_sp500() if files exist
        - Calls download_sp500() if files are missing

    Examples:
        >>> spy, sp500 = safe_load()
    """
    fp1 = "./spy_1999.csv"
    fp2 = "./sp500_1999.csv"
    if os.path.exists(fp1) and os.path.exists(fp2):
        return restore_sp500()
    else:
        return download_sp500()


spy_data, sp500_data = safe_load()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--download":
        download_sp500()
    # else:
    #     load_data()
