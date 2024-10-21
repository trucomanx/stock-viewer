#!/usr/bin/python3
import os
import json

DEFAULT_CONFIG_STRING='''
{
    "columns": [
        {"key":"stock",              "title":"Stock",          "tooltip":"Etiqueta da ação em yahoo finance"},
        {"key":"quantity",           "title":"Qtty",           "tooltip":"Quantidade de ações"},
        {"key":"average_price",      "title":"P. Médio",       "tooltip":"Preço medio da ação"},
        {"key":"currentPrice",       "title":"P. Atual",       "tooltip":"Preço atual da ação"},
        {"key":"initial_amount",     "title":"V. Inicial",     "tooltip":"Valor incial médio do capital"},
        {"key":"total_amount",       "title":"V. Total",       "tooltip":"Total do capital"},
        {"key":"capital_gain",       "title":"Ganho",          "tooltip":"Ganho do capital"},
        {"key":"capital_gain_ratio", "title":"Ganho%",         "tooltip":"Ganho do capital%"},
        {"key":"longName",           "title":"Nome",           "tooltip":"Nome da ação"},
        {"key":"dividendYield",      "title":"DY%",            "tooltip":"Dividend yield by year in %"},
        {"key":"fiveYearAvgDividendYield","title":"5DY%",      "tooltip":"5 year average dividend yield by year in%"},
        {"key":"forwardPE",          "title":"Forward P/E",    "tooltip":"Preço por ação sobre Ganho por ação prospectivo"},
        {"key":"trailingEps",        "title":"Trailing EPS",   "tooltip":"Lucro por Ação Retrospectivo"},
        {"key":"pegRatio",           "title":"PEG Ratio",      "tooltip":"PE ratio sobre taxa de crecimento"},
        {"key":"bookValue",          "title":"VPA",            "tooltip":"Valor patrimonial por ação"},
        {"key":"priceToBook",        "title":"P/VP",           "tooltip":"Preço sobre o valor patrimonial"},
        {"key":"returnOnEquity",     "title":"ROE%",           "tooltip":"Retorno sobre o investimento%"},
        {"key":"payoutRatio",        "title":"Payout%",        "tooltip":"Payout ratio%"},
        {"key":"profitMargins",      "title":"ProfitMargins%", "tooltip":"Lucro liquido sobre receita total%"},
        {"key":"sector",             "title":"Sector",         "tooltip":"Sector"}, 
        {"key":"industry",           "title":"Industry",       "tooltip":"Industry"}
    ]
}
'''

DEFAULT_CONFIG_PATH='~/.config/stock-viewer/default.stock-viewer.conf.json'

def load_default_config_file():
    print(f"Creating the default config file: {DEFAULT_CONFIG_PATH}")
    
    config_path = os.path.expanduser(DEFAULT_CONFIG_PATH)
    directory = os.path.dirname(config_path)
    
    os.makedirs(directory,exist_ok=True)
    
    # Abrindo (ou criando) um arquivo para escrita
    with open(config_path, "w") as file:
        # Escrevendo a string no arquivo
        file.write(DEFAULT_CONFIG_STRING)

    with open(config_path, 'r') as file:
        config_data = json.load(file)
        if len(config_data["columns"])==0:
            print("Exit because problems loading config file: {DEFAULT_CONFIG_PATH}")
            exit();
    return config_data,DEFAULT_CONFIG_PATH



def load_json_config_file(config_path):
    config_path = os.path.expanduser(config_path)
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
            if len(config_data["columns"])==0:
                print("Problems loading config file")
                exit();
        
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found.")
        config_data, config_path = load_default_config_file()
    
    except json.JSONDecodeError:
        print(f"Error reading configuration file {config_path}.")
        config_data, config_path = load_default_config_file()
    
    return config_data, config_path;
