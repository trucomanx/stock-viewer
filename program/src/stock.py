#!/usr/bin/python

# pip install yfinance
import yfinance as yf

# Definir o símbolo da ação
symbol = 'AAPL'  # Substitua pelo símbolo que deseja obter

# Criar o objeto Ticker
stock = yf.Ticker(symbol)

# Obter informações fundamentais
info = stock.info

# Mostrar alguns dados fundamentais
print("current price:", info.get('currentPrice', 'N/A'))
print("Nome da empresa:", info['longName'])
print("Dividendo Yield:", info.get('dividendYield', 'N/A'))
print("P/E Ratio:", info.get('forwardPE', 'N/A'))
print("Valor de Mercado:", info.get('marketCap', 'N/A'))
print("Volume médio:", info.get('averageVolume', 'N/A'))

