#!/usr/bin/python

# pip install yfinance
import yfinance as yf


def agregate_more_stock_info(stocks_data):
    for stock_name in stocks_data:
        # Criar o objeto Ticker
        stock = yf.Ticker(stock_name)
        
        
        # currentPrice
        stocks_data[stock_name]['currentPrice']=stock.info.get('currentPrice', float("nan"))
        
        # total_amount
        stocks_data[stock_name]['total_amount']=stocks_data[stock_name]['currentPrice']*stocks_data[stock_name]['quantity'];
        
        # initial_amount
        stocks_data[stock_name]['initial_amount']=stocks_data[stock_name]['average_price']*stocks_data[stock_name]['quantity'];
        
        # capital_gain
        stocks_data[stock_name]['capital_gain']=stocks_data[stock_name]['total_amount']-stocks_data[stock_name]['initial_amount'];
        
        # longName
        stocks_data[stock_name]['longName']=stock.info.get('longName', 'N/A')
        
        # dividendYield
        stocks_data[stock_name]['dividendYield']=stock.info.get('dividendYield', float("nan"))
        
        # forwardPE
        stocks_data[stock_name]['forwardPE']=stock.info.get('forwardPE', float("nan"))
        
        # bookValue
        stocks_data[stock_name]['bookValue']=stock.info.get('bookValue', float("nan"))
        
        # priceToBook
        stocks_data[stock_name]['priceToBook']=stock.info.get('priceToBook', float("nan"))
        
        # returnOnEquity
        stocks_data[stock_name]['returnOnEquity']=stock.info.get('returnOnEquity', float("nan"))
        
        # payoutRatio
        stocks_data[stock_name]['payoutRatio']=stock.info.get('payoutRatio', float("nan"))

        #print("Valor de Mercado:", stock.info.get('marketCap', 'N/A'))
        #print("Volume médio:", stock.info.get('averageVolume', 'N/A'))
        
    return stocks_data;
