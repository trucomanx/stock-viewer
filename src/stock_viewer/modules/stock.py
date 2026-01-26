#!/usr/bin/python

# pip install yfinance curl-cffi
import yfinance as yf
import json
import math
import pandas as pd
import numpy as np
import time
import tempfile
import os

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication

temp_dir = tempfile.gettempdir()
yf.set_tz_cache_location(os.path.join(temp_dir, "yf_cache"))

# ---------------- PRICE HISTORY ---------------- #

def price_hist(stock, period="6mo", interval="1d"):
    for p in [period, "5d"]:
        try:
            hist = stock.history(period=p, interval="1d")

            if hist is None or hist.empty:
                continue

            if "Adj Close" in hist.columns:
                prices = hist["Adj Close"].dropna().tolist()
            else:
                prices = hist["Close"].dropna().tolist()

            if prices:
                return prices

        except Exception:
            continue

    return []

# ---------------- CURRENT PRICE ---------------- #

def get_current_price(stock):
    try:
        price = stock.fast_info.get("last_price")
        if isinstance(price, (int, float)):
            return price
    except Exception:
        pass

    try:
        hist = price_hist(stock, period="1d", interval="1m")
        
        if len(hist)>0:
            return float(hist[-1])
    except Exception:
        pass

    return float("nan")

# ---------------- DIVIDENDS ---------------- #

def get_dividend_yield(stock, info):
    try:
        dy = info.get("dividendYield")
        if isinstance(dy, (int, float)) and dy > 0:
            return dy
    except Exception:
        pass

    try:
        dividends = stock.dividends
        if dividends is None or dividends.empty:
            return float("nan")

        dividends_ttm = dividends.last("365D").sum()
        price = get_current_price(stock)

        if price > 0:
            return dividends_ttm / price
    except Exception:
        pass

    return float("nan")

def get_five_year_avg_dividend_yield(stock, info):
    try:
        dy5 = info.get("fiveYearAvgDividendYield")
        if isinstance(dy5, (int, float)) and dy5 > 0:
            return dy5
    except Exception:
        pass

    try:
        dividends = stock.dividends
        if dividends is None or dividends.empty:
            return float("nan")

        df = pd.DataFrame({"dividend": dividends})
        yearly_div = df["dividend"].resample("Y").sum()

        prices = price_hist(stock, period="5y")
        yearly_price = np.mean(prices)

        merged = pd.concat([yearly_div, pd.Series(yearly_price)], axis=1)
        merged.columns = ["dividend", "price"]
        merged = merged.dropna()

        if merged.empty:
            return float("nan")

        merged["yield"] = merged["dividend"] / merged["price"]
        valid_years = merged["yield"].replace(0, np.nan).dropna()

        if len(valid_years) < 2:
            return float("nan")

        return float(valid_years.mean())

    except Exception:
        return float("nan")

# ---------------- PE / PEG ---------------- #

def get_forward_pe(stock, info):
    try:
        pe = info.get("forwardPE")
        if isinstance(pe, (int, float)) and pe > 0:
            return pe
    except Exception:
        pass

    try:
        eps_fwd = info.get("forwardEps")
        price = get_current_price(stock)

        if isinstance(eps_fwd, (int, float)) and eps_fwd > 0 and price > 0:
            return price / eps_fwd
    except Exception:
        pass

    return float("nan")

def get_peg_ratio(stock, info, years=3):
    peg = info.get("pegRatio")
    if isinstance(peg, (int, float)) and peg > 0:
        return float(peg)

    try:
        pe = info.get("trailingPE")
        if pe is None or pe <= 0:
            return math.nan

        income = stock.income_stmt
        if income is None or income.empty:
            return math.nan

        if "Net Income" not in income.index:
            return math.nan

        net_income = income.loc["Net Income"].dropna()

        if len(net_income) < years + 1:
            return math.nan

        ni_start = net_income.iloc[-(years + 1)]
        ni_end = net_income.iloc[-1]

        if ni_start <= 0 or ni_end <= 0:
            return math.nan

        growth = (ni_end / ni_start) ** (1 / years) - 1
        if growth <= 0:
            return math.nan

        return pe / (growth * 100)

    except Exception:
        return math.nan

# ---------------- LONG NAME ---------------- #

def get_long_name(stock, info):
    try:
        name = info.get("longName") or info.get("shortName")
        if isinstance(name, str) and name.strip():
            return name.strip()
    except Exception:
        pass

    try:
        fi = stock.fast_info
        if isinstance(fi, dict):
            name = fi.get("shortName")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception:
        pass

    ticker = getattr(stock, "ticker", "N/A")

    if ticker.endswith(".SA"):
        return f"{ticker.replace('.SA','')} (B3)"

    return ticker

# ---------------- MAIN ---------------- #

def agregate_more_stock_info(stocks_data, progress=None, parent=None):
    if progress is not None:
        progress.setMaximum(len(stocks_data))

    k = 0

    for stock_name in stocks_data:
        try:
            stock = yf.Ticker(stock_name)

            try:
                info = stock.get_info() or {}
            except Exception:
                info = {}

            if progress is not None:
                QApplication.processEvents()
                progress.setValue(k + 1)

            stocks_data[stock_name]['currentPrice'] = get_current_price(stock)

            stocks_data[stock_name]['total_amount'] = (
                stocks_data[stock_name]['currentPrice'] * stocks_data[stock_name]['quantity']
            )

            stocks_data[stock_name]['initial_amount'] = (
                stocks_data[stock_name]['average_price'] * stocks_data[stock_name]['quantity']
            )

            stocks_data[stock_name]['capital_gain'] = (
                stocks_data[stock_name]['total_amount'] - stocks_data[stock_name]['initial_amount']
            )

            try:
                stocks_data[stock_name]['capital_gain_ratio'] = (
                    stocks_data[stock_name]['capital_gain'] / stocks_data[stock_name]['initial_amount']
                )
            except Exception:
                stocks_data[stock_name]['capital_gain_ratio'] = 0.0

            stocks_data[stock_name]['longName'] = get_long_name(stock, info)

            stocks_data[stock_name]['dividendYield'] = get_dividend_yield(stock, info)

            stocks_data[stock_name]['fiveYearAvgDividendYield'] = get_five_year_avg_dividend_yield(stock, info)

            stocks_data[stock_name]['profitMargins'] = info.get('profitMargins', float("nan"))

            stocks_data[stock_name]['forwardPE'] = get_forward_pe(stock, info)

            stocks_data[stock_name]['pegRatio'] = get_peg_ratio(stock, info)

            stocks_data[stock_name]['trailingEps'] = info.get('trailingEps', float("nan"))

            stocks_data[stock_name]['bookValue'] = info.get('bookValue', float("nan"))

            stocks_data[stock_name]['priceToBook'] = info.get('priceToBook', float("nan"))

            stocks_data[stock_name]['returnOnEquity'] = info.get('returnOnEquity', float("nan"))

            stocks_data[stock_name]['payoutRatio'] = info.get('payoutRatio', float("nan"))

            stocks_data[stock_name]['industry'] = info.get('industry', 'N/A')

            stocks_data[stock_name]['sector'] = info.get('sector', 'N/A')

            stocks_data[stock_name]["currency"] = info.get("currency", 'N/A')

            stocks_data[stock_name]["daysData2y"] = price_hist(stock, period="2y")

            stocks_data[stock_name]["daysData6mo"] = price_hist(stock, period="6mo")

            stocks_data[stock_name]["daysData1mo"] = price_hist(stock, period="1mo")

            time.sleep(0.4)

        except Exception as e:
            print(f"Error {stock_name}: {e}")

            if parent is not None:
                QMessageBox.critical(parent, "Error getting data", f"{stock_name}:\n\n{str(e)}")

        k += 1

    return stocks_data

# ---------------- TEST ---------------- #

if __name__ == "__main__":
    stock = yf.Ticker("CPFE3.SA")
    print(json.dumps(stock.get_info(), indent=4))

