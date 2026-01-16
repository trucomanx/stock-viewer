#!/usr/bin/python

# pip install yfinance
import yfinance as yf
import json

from PyQt5.QtWidgets import  QApplication

def price_hist(stock,period="6mo"):
    try:
        hist = stock.history(period=period, interval="1d")

        # usa preço de fechamento ajustado se existir
        if "Adj Close" in hist:
            prices = hist["Adj Close"].dropna().tolist()
        else:
            prices = hist["Close"].dropna().tolist()

    except Exception as e:
        # fallback seguro
        prices = []
    return prices

def agregate_more_stock_info(stocks_data,progress=None):
    if progress is not None:
        progress.setMaximum(len(stocks_data));
    
    k=0;
    for stock_name in stocks_data:
        # Criar o objeto Ticker
        stock = yf.Ticker(stock_name)
        
        if progress is not None:
            QApplication.processEvents()  # Permite que a interface responda
            progress.setValue(k+1);
        # currentPrice
        stocks_data[stock_name]['currentPrice']=stock.info.get('currentPrice', float("nan"))
        
        # total_amount
        stocks_data[stock_name]['total_amount']=stocks_data[stock_name]['currentPrice']*stocks_data[stock_name]['quantity'];
        
        # initial_amount
        stocks_data[stock_name]['initial_amount']=stocks_data[stock_name]['average_price']*stocks_data[stock_name]['quantity'];
        
        # capital_gain
        stocks_data[stock_name]['capital_gain']=stocks_data[stock_name]['total_amount']-stocks_data[stock_name]['initial_amount'];
        
        # capital_gain ratio
        stocks_data[stock_name]['capital_gain_ratio']=(stocks_data[stock_name]['total_amount']-stocks_data[stock_name]['initial_amount'])/stocks_data[stock_name]['initial_amount'];
        
        # longName
        stocks_data[stock_name]['longName']=stock.info.get('longName', 'N/A')
        
        # dividendYield
        stocks_data[stock_name]['dividendYield']=stock.info.get('dividendYield', float("nan"))
        
        # fiveYearAvgDividendYield
        stocks_data[stock_name]['fiveYearAvgDividendYield']=stock.info.get('fiveYearAvgDividendYield', float("nan"))
        
        # profitMargins
        stocks_data[stock_name]['profitMargins']=stock.info.get('profitMargins', float("nan"))
        
        # forwardPE
        stocks_data[stock_name]['forwardPE']=stock.info.get('forwardPE', float("nan"))
        
        # pegRatio
        stocks_data[stock_name]['pegRatio']=stock.info.get('pegRatio', float("nan"))
        
        # trailingEps
        stocks_data[stock_name]['trailingEps']=stock.info.get('trailingEps', float("nan"))
        
        # bookValue
        stocks_data[stock_name]['bookValue']=stock.info.get('bookValue', float("nan"))
        
        # priceToBook
        stocks_data[stock_name]['priceToBook']=stock.info.get('priceToBook', float("nan"))
        
        # returnOnEquity
        stocks_data[stock_name]['returnOnEquity']=stock.info.get('returnOnEquity', float("nan"))
        
        # payoutRatio
        stocks_data[stock_name]['payoutRatio']=stock.info.get('payoutRatio', float("nan"))
        
        # industry
        stocks_data[stock_name]['industry']=stock.info.get('industry', 'N/A')
        
        # sector
        stocks_data[stock_name]['sector']=stock.info.get('sector', 'N/A')
        
        # currency
        stocks_data[stock_name]["currency"]=stock.info.get("currency", 'N/A')

        # daysData6mo:
        stocks_data[stock_name]["daysData2y"] = price_hist(stock,period="2y")

        # daysData6mo:
        stocks_data[stock_name]["daysData6mo"] = price_hist(stock,period="6mo")
        
        # daysData1mo:
        stocks_data[stock_name]["daysData1mo"] = price_hist(stock,period="1mo")

        #print("Valor de Mercado:", stock.info.get('marketCap', 'N/A'))
        #print("Volume médio:", stock.info.get('averageVolume', 'N/A'))
        
        k=k+1;
        
    return stocks_data;


if __name__ == "__main__":
    stock = yf.Ticker("CPFE3.SA")
    print(json.dumps(stock.info, indent=4))
