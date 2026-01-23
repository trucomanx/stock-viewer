#!/usr/bin/python

# pip install yfinance
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

def price_hist(stock, period="6mo"):
    for p in [period, "5d"]:
        try:
            hist = stock.history(period=p, interval="1d")

            if hist is None or hist.empty:
                continue

            # usa preço de fechamento ajustado se existir
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

    # 2️⃣ info (instável)
    try:
        price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice")
        if isinstance(price, (int, float)):
            return price
    except Exception:
        pass

    # 1️⃣ fast_info (mais confiável)
    try:
        price = stock.fast_info.get("last_price")
        if isinstance(price, (int, float)):
            return price
    except Exception:
        pass


    # 3️⃣ histórico (último recurso)
    try:
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass

    return float("nan")

# ---------------- DIVIDENDS ---------------- #

def get_dividend_yield(stock):
    # 1️⃣ tenta direto do info (se existir)
    try:
        dy = stock.info.get("dividendYield")
        if isinstance(dy, (int, float)) and dy > 0:
            return dy
    except Exception:
        pass

    # 2️⃣ calcula manualmente (TTM)
    try:
        dividends = stock.dividends
        if dividends is None or dividends.empty:
            return float("nan")

        dividends_ttm = dividends.last("365D").sum()

        price = get_current_price(stock)
        if not isinstance(price, (int, float)) or price <= 0:
            return float("nan")

        if price > 0:
            return dividends_ttm / price
    except Exception:
        pass

    return float("nan")

def get_five_year_avg_dividend_yield(stock):
    # 1️⃣ usa Yahoo se existir
    try:
        dy5 = stock.info.get("fiveYearAvgDividendYield")
        if isinstance(dy5, (int, float)) and dy5 > 0:
            return dy5
    except Exception:
        pass

    # 2️⃣ fallback: cálculo manual flexível
    try:
        dividends = stock.dividends
        if dividends is None or dividends.empty:
            return float("nan")

        df = pd.DataFrame({"dividend": dividends})

        # agrega dividendos por ano (sem exigir todos os anos)
        yearly_div = df["dividend"].resample("Y").sum()

        prices = price_hist(stock, period="5y")
        yearly_price = np.mean(prices)

        merged = pd.concat([yearly_div, yearly_price], axis=1)
        merged.columns = ["dividend", "price"]
        merged = merged.dropna(subset=["price"])

        if merged.empty:
            return float("nan")

        merged["yield"] = merged["dividend"] / merged["price"]

        # aceita anos com dividendos zero
        valid_years = merged["yield"].replace(0, np.nan).dropna()

        # exige pelo menos 2 anos válidos
        if len(valid_years) < 2:
            return float("nan")

        return float(valid_years.mean())
    except Exception:
        return float("nan")

# ---------------- PE / PEG ---------------- #

def get_forward_pe(stock):
    # 1️⃣ Yahoo (se existir)
    try:
        pe = stock.info.get("forwardPE")
        if isinstance(pe, (int, float)) and pe > 0:
            return pe
    except Exception:
        pass

    # 2️⃣ fallback: calcular se possível
    try:
        eps_fwd = stock.info.get("forwardEps")
        price = get_current_price(stock)

        if (
            isinstance(eps_fwd, (int, float))
            and eps_fwd > 0
            and isinstance(price, (int, float))
        ):
            return price / eps_fwd
    except Exception:
        pass

    return float("nan")

def get_peg_ratio(stock, years=3):
    """
    Retorna o PEG Ratio.
    1) Usa pegRatio do Yahoo se existir
    2) Caso contrário, calcula via crescimento histórico do lucro líquido
    """

    info = stock.info

    # 1) Tentativa direta (Yahoo)
    peg = info.get("pegRatio")
    if peg is not None and peg > 0:
        return float(peg)

    try:
        # P/E
        pe = info.get("trailingPE")
        if pe is None or pe <= 0:
            return math.nan

        # Demonstrativo de resultados
        income = stock.income_stmt

        if income is None or income.empty:
            return math.nan

        # Linha correta segundo Yahoo
        if "Net Income" not in income.index:
            return math.nan

        net_income = income.loc["Net Income"].dropna()

        if len(net_income) < years + 1:
            return math.nan

        # CAGR do lucro
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

def get_long_name(stock):
    # 1️⃣ info (se existir)
    try:
        info = stock.info
        if isinstance(info, dict):
            name = info.get("longName") or info.get("shortName")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception:
        pass

    # 2️⃣ fast_info (às vezes tem)
    try:
        fi = stock.fast_info
        if isinstance(fi, dict):
            name = fi.get("shortName")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception:
        pass

    # 3️⃣ metadata do history (bem frágil, mas ajuda)
    try:
        meta = getattr(stock, "_history_metadata", None)
        if isinstance(meta, dict):
            symbol = meta.get("symbol")
            exchange = meta.get("exchangeName")
            if symbol and exchange:
                return f"{symbol} ({exchange})"
    except Exception:
        pass

    # 4️⃣ fallback final: nome “humano” a partir do ticker
    ticker = getattr(stock, "ticker", "N/A")

    if ticker.endswith(".SA"):
        base = ticker.replace(".SA", "")
        return f"{base} (B3)"

    return ticker

# ---------------- MAIN AGGREGATOR ---------------- #

def agregate_more_stock_info(stocks_data, progress=None, parent=None):
    if progress is not None:
        progress.setMaximum(len(stocks_data))

    k = 0

    for stock_name in stocks_data:
        try:
            # Criar o objeto Ticker
            stock = yf.Ticker(stock_name)
            
            info = stock.info
            if info is None:
                print(f"Atention: stock.info for '{stock_name}' return None. Skipping fields dependent on the info.")
                info = {}  # usar dict vazio para evitar AttributeError
            
            if progress is not None:
                QApplication.processEvents()  # Permite que a interface responda
                progress.setValue(k+1);
            # currentPrice
            stocks_data[stock_name]['currentPrice']=get_current_price(stock) #stock.info.get('currentPrice', float("nan"))
            
            # total_amount
            stocks_data[stock_name]['total_amount']=stocks_data[stock_name]['currentPrice']*stocks_data[stock_name]['quantity'];
            
            # initial_amount
            stocks_data[stock_name]['initial_amount']=stocks_data[stock_name]['average_price']*stocks_data[stock_name]['quantity'];
            
            # capital_gain
            stocks_data[stock_name]['capital_gain']=stocks_data[stock_name]['total_amount']-stocks_data[stock_name]['initial_amount'];
            
            # capital_gain ratio
            try:
                stocks_data[stock_name]['capital_gain_ratio']=(stocks_data[stock_name]['total_amount']-stocks_data[stock_name]['initial_amount'])/stocks_data[stock_name]['initial_amount'];
            except Exception:
                stocks_data[stock_name]['capital_gain_ratio']=0.0;
            
            
            # longName
            stocks_data[stock_name]['longName']=get_long_name(stock)
            
            # dividendYield
            stocks_data[stock_name]['dividendYield']=get_dividend_yield(stock)
            
            # fiveYearAvgDividendYield
            stocks_data[stock_name]['fiveYearAvgDividendYield']=get_five_year_avg_dividend_yield(stock)
            
            # profitMargins
            stocks_data[stock_name]['profitMargins']=info.get('profitMargins', float("nan"))
            
            # forwardPE
            stocks_data[stock_name]['forwardPE']=get_forward_pe(stock)
            
            # pegRatio
            stocks_data[stock_name]['pegRatio']=get_peg_ratio(stock)
            
            # trailingEps
            stocks_data[stock_name]['trailingEps']=info.get('trailingEps', float("nan"))
            
            # bookValue
            stocks_data[stock_name]['bookValue']=info.get('bookValue', float("nan"))
            
            # priceToBook
            stocks_data[stock_name]['priceToBook']=info.get('priceToBook', float("nan"))
            
            # returnOnEquity
            stocks_data[stock_name]['returnOnEquity']=info.get('returnOnEquity', float("nan"))
            
            # payoutRatio
            stocks_data[stock_name]['payoutRatio']=info.get('payoutRatio', float("nan"))
            
            # industry
            stocks_data[stock_name]['industry']=info.get('industry', 'N/A')
            
            # sector
            stocks_data[stock_name]['sector']=info.get('sector', 'N/A')
            
            # currency
            stocks_data[stock_name]["currency"]=info.get("currency", 'N/A')

            # daysData6mo:
            stocks_data[stock_name]["daysData2y"] = price_hist(stock,period="2y")

            # daysData6mo:
            stocks_data[stock_name]["daysData6mo"] = price_hist(stock,period="6mo")
            
            # daysData1mo:
            stocks_data[stock_name]["daysData1mo"] = price_hist(stock,period="1mo")

            #print("Valor de Mercado:", info.get('marketCap', 'N/A'))
            #print("Volume médio:", info.get('averageVolume', 'N/A'))
            time.sleep(1)  # espera 1 segundo entre requisições
        except Exception as e:
            print(f"Error {stock_name}: {e}")
            
            if parent is not None:
                QMessageBox.critical(
                    parent,
                    "Error getting data",
                    f"{stock_name}:\n\n{str(e)}"
                )
            
        k += 1

    return stocks_data


if __name__ == "__main__":
    stock = yf.Ticker("CPFE3.SA")
    print(json.dumps(stock.info, indent=4))
