#!/usr/bin/python3

import sys
import json
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QTableWidget, 
    QTableWidgetItem, QWidget, QPushButton, QLineEdit, QFileDialog, QHBoxLayout, 
    QTabWidget, QFormLayout
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from stock import agregate_more_stock_info

DEFAULT_CONFIG_PATH='base.stock-viewer.conf.json'


# Subclassificando QTableWidgetItem para suportar ordenação numérica
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        # Verifica se ambos os itens podem ser convertidos para número, se sim, compara numericamente
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            # Se não puder ser convertido em número, compara como strings
            return super().__lt__(other)
            
def dicts_to_keys_titles(lista):
    list_keys=[];
    list_titles=[];
    list_tooltips=[];
    for d in lista:
        list_keys.append(d['key'])
        list_titles.append(d['title'])
        list_tooltips.append(d['tooltip'])
    return list_keys,list_titles,list_tooltips
        

class StocksViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stocks Viewer')
        self.setGeometry(100, 100, 1000, 600)

        self.stocks_data = {}
        self.groups_data = {}
        self.config_data = {}


        self.initUI()
        self.config_data=self.load_config_file(DEFAULT_CONFIG_PATH);

        self.column_keys, self.column_titles, self.column_tooltips = dicts_to_keys_titles(self.config_data["columns"])


    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.table_tab = QWidget()
        self.config_tab = QWidget()

        self.tab_widget.addTab(self.table_tab, 'Data Visualization')
        self.tab_widget.addTab(self.config_tab, 'Settings')

        self.setup_table_tab()
        self.setup_config_tab()

        layout.addWidget(self.tab_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def setup_table_tab(self):
        layout = QVBoxLayout()

        # Layout horizontal para stocks.json
        stocks_layout = QHBoxLayout()
        self.stocks_path_edit = QLineEdit(self)
        self.stocks_path_edit.setPlaceholderText('Select *.stocks.json')
        self.stocks_path_edit.setToolTip('Path to the stocks.json file that contains the stock data')
        stocks_layout.addWidget(self.stocks_path_edit)

        self.stocks_button = QPushButton('Select *.stocks.json', self)
        self.stocks_button.setToolTip('Click to select the *.stocks.json file')
        self.stocks_button.clicked.connect(self.select_stocks_file)
        stocks_layout.addWidget(self.stocks_button)

        layout.addLayout(stocks_layout)

        # Layout horizontal para groups.json
        groups_layout = QHBoxLayout()
        self.groups_path_edit = QLineEdit(self)
        self.groups_path_edit.setPlaceholderText('Select *.groups.json')
        self.groups_path_edit.setToolTip('Path to the groups.json file that contains the action groups')
        groups_layout.addWidget(self.groups_path_edit)

        self.groups_button = QPushButton('Select *.groups.json', self)
        self.groups_button.setToolTip('Click to select the *.groups.json file')
        self.groups_button.clicked.connect(self.select_groups_file)
        groups_layout.addWidget(self.groups_button)

        layout.addLayout(groups_layout)

        # Botão de Atualizar
        self.update_button = QPushButton('To update', self)
        self.update_button.setToolTip('Click to update data for selected files')
        self.update_button.clicked.connect(self.update_data)
        layout.addWidget(self.update_button)

        # Botão de Salvar
        self.save_button = QPushButton('Save', self)
        self.save_button.setToolTip('Click to save changes made to stock data')
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(self.save_button)

        # Label
        self.label = QLabel('Select a group of actions:')
        layout.addWidget(self.label)

        # ComboBox para selecionar o grupo
        self.comboBox = QComboBox()
        self.comboBox.setToolTip('Choose a stock group to view its details')
        self.comboBox.currentTextChanged.connect(self.display_table)
        layout.addWidget(self.comboBox)

        # Tabela para mostrar os stocks
        self.tableWidget = QTableWidget()
        self.tableWidget.setToolTip('Table displaying the shares, average prices, quantities and total amounts of the selected group')
        self.tableWidget.setSortingEnabled(True)# Habilitar a ordenação ao clicar nos títulos das colunas
        self.tableWidget.itemChanged.connect(self.callback_item_changed)
        layout.addWidget(self.tableWidget)

        # Label para mostrar o montante total do grupo
        self.total_label = QLabel('Total Group Amount: ')
        self.total_label.setToolTip('Shows the total amount invested in the selected stock group')
        layout.addWidget(self.total_label)

        self.table_tab.setLayout(layout)

    def setup_config_tab(self):
        layout = QFormLayout()

        # Layout horizontal para config.json
        self.config_path_edit = QLineEdit(self)
        self.config_path_edit.setPlaceholderText('Select the *.stock-viewer.conf.json file')
        self.config_path_edit.setToolTip('Path to the stock-viewer.conf.json file that contains the columns configuration')
        layout.addRow('Configuration File:', self.config_path_edit)

        self.config_button = QPushButton('Select Configuration', self)
        self.config_button.setToolTip('Click to select the *.stock-viewer.conf.json file')
        self.config_button.clicked.connect(self.select_config_file)
        layout.addRow('', self.config_button)

        # Botão de Atualizar Configuração
        self.update_config_button = QPushButton('Update Configuration', self)
        self.update_config_button.setToolTip('Click to update the column configuration in the table')
        self.update_config_button.clicked.connect(self.update_table_columns)
        layout.addRow('', self.update_config_button)

        self.config_tab.setLayout(layout)

    def select_stocks_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select the stocks.json file', '', 'Stocks JSON Files (*.stocks.json)')
        if path:
            self.stocks_path_edit.setText(path)

    def select_groups_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select the groups.json file', '', 'Groups JSON Files (*.groups.json)')
        if path:
            self.groups_path_edit.setText(path)

    def select_config_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select the stock-viewer.conf.json file', '', 'Config JSON Files (*.stock-viewer.conf.json)')
        if path:
            self.config_path_edit.setText(path)

    def load_config_file(self,default_config_path):
        try:
            with open(default_config_path, 'r') as file:
                config_data = json.load(file)
                if len(config_data["columns"])==0:
                    print("Problems loading config file")
                    exit();
            self.config_path_edit.setText(default_config_path)
        except FileNotFoundError:
            print(f"Default configuration file {default_config_path} not found.")
            exit();
        except json.JSONDecodeError:
            print(f"Error reading default configuration file {default_config_path}.")
            exit();
        return config_data;

    def update_data(self):
        stocks_path = self.stocks_path_edit.text()
        groups_path = self.groups_path_edit.text()

        if stocks_path:
            self.stocks_data = self.load_json(stocks_path)

        if groups_path:
            self.groups_data = self.load_json(groups_path)


        self.stocks_data=agregate_more_stock_info(self.stocks_data)
        self.populate_groups()
        
        self.display_table(self.comboBox.currentText())
        self.update_color_currentPrices()

    def update_table_columns(self):
        config_path = self.config_path_edit.text()

        if not config_path:
            return

        self.config_data=self.load_config_file(config_path);
        self.column_keys, self.column_titles = dicts_to_keys_titles(self.config_data["columns"])
        
        self.display_table(self.comboBox.currentText())

    def load_json(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)

    def save_data(self):
        stocks_path = self.stocks_path_edit.text()

        if not stocks_path:
            return

        dict_to_save=dict()
        
        for stock_name in self.stocks_data:
            dict_to_save[stock_name] = {
                'average_price': self.stocks_data[stock_name]["average_price"],
                'quantity':      self.stocks_data[stock_name]["quantity"]
            }
        
        
        # Salva os dados atualizados de volta no arquivo JSON
        with open(stocks_path, 'w') as file:
            json.dump(dict_to_save, file, indent=4)

    def populate_groups(self):
        self.comboBox.clear()
        self.comboBox.addItems(self.groups_data.keys())
        self.display_table(self.comboBox.currentText())

    def display_table(self, group_name):
        if not group_name or group_name not in self.groups_data:
            return

        group_stocks = self.groups_data[group_name]
        total_group_amount = 0

        # Configuração de colunas

        self.tableWidget.setColumnCount(len(self.column_titles))
        self.tableWidget.setHorizontalHeaderLabels(self.column_titles)
        
        # Adicionar os tooltips em todas as colunas
        for i in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(i)  # Obter o item do cabeçalho
            header_item.setToolTip(self.column_tooltips[i])

        self.tableWidget.setRowCount(len(group_stocks))

        for row, stock in enumerate(group_stocks):
            stock_data = self.stocks_data.get(stock, {})
            
            
            for col, column in enumerate(self.column_keys):
                if column == "stock":
                    item = QTableWidgetItem(stock)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "average_price":
                    value = stock_data.get('average_price', 0)
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    
                elif column == "quantity":
                    value = stock_data.get('quantity', 0)
                    item = NumericTableWidgetItem(f'{value}')
                    
                elif column == "total_amount":
                    value = stock_data.get('total_amount', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "capital_gain":
                    value = stock_data.get('capital_gain', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "currentPrice":
                    value = stock_data.get('currentPrice', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "longName":
                    value = stock_data.get('longName', '') 
                    item = QTableWidgetItem(f'{value}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "dividendYield":
                    value = stock_data.get('dividendYield', float("nan")) 
                    item = NumericTableWidgetItem(f'{value*100.0:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "forwardPE":
                    value = stock_data.get('forwardPE', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "bookValue":
                    value = stock_data.get('bookValue', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "priceToBook":
                    value = stock_data.get('priceToBook', float("nan")) 
                    item = NumericTableWidgetItem(f'{value:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "returnOnEquity":
                    value = stock_data.get('returnOnEquity', float("nan")) 
                    item = NumericTableWidgetItem(f'{value*100.0:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                elif column == "payoutRatio":
                    value = stock_data.get('payoutRatio', float("nan")) 
                    item = NumericTableWidgetItem(f'{value*100.0:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                    
                else:
                    item = QTableWidgetItem('')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável

                # Define a cor de fundo para as células não editáveis
                if not (item.flags() & Qt.ItemIsEditable):
                    item.setBackground(QColor('lightgray'))

                self.tableWidget.setItem(row, col, item)

            # Atualizar o montante total do grupo
            total_group_amount += stock_data.get('total_amount', 0) 

        self.total_label.setText(f'Montante Total do Grupo: {total_group_amount:.2f}')
        self.update_color_currentPrices()



    def update_color_currentPrice(self, row):
        price_current_item = self.tableWidget.item(row, self.column_keys.index('currentPrice'))  # Coluna 'Preço Atual'
        price_mean_item    = self.tableWidget.item(row, self.column_keys.index('average_price'))  # Coluna 'Preço Médio'
        
        if price_current_item and price_mean_item:
            # Atualiza a cor da célula com base no preço
            price_mean   = float(price_mean_item.text())
            currentPrice = float(price_current_item.text())
            
            if currentPrice > price_mean:
                price_current_item.setBackground(QColor('green'))
            else:
                price_current_item.setBackground(QColor('red')) 
    
    def update_color_currentPrices(self):
        for row in range(self.tableWidget.rowCount()):
            self.update_color_currentPrice( row)


    def callback_item_changed(self, item):
        id_stock = self.column_keys.index('stock')
        id_avr   = self.column_keys.index('average_price')
        id_qtty  = self.column_keys.index('quantity')
        
        row = item.row()
        col = item.column()
        
        stock_name         = self.tableWidget.item(row, id_stock).text()
        
        average_price_item = self.tableWidget.item(row, id_avr)
        quantity_item      = self.tableWidget.item(row, id_qtty)
        
        quantity      = 0
        average_price = 0.0
        if average_price_item:
            average_price = float(average_price_item.text())
        if quantity_item:
            quantity = int(quantity_item.text())
        
        
        ## average_price in stock_data
        if col == id_avr:
            self.update_color_currentPrice(row)
            self.stocks_data[stock_name]["average_price"]=average_price
            
        ## average_price in stock_data
        if col == id_qtty:
            self.stocks_data[stock_name]["quantity"]=quantity
        
        ## total_amount in stock_data
        if col == id_qtty:  # Apenas colunas de quantity e preço médio
            #print(self.stocks_data[stock_name])
            total_amount = quantity * self.stocks_data[stock_name]['currentPrice']
            self.stocks_data[stock_name]["total_amount"]=total_amount
            
            total_amount_item = self.tableWidget.item(row, self.column_keys.index('total_amount'))
            if total_amount_item:
                total_amount_item.setText(f'{total_amount:.2f}')

                    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = StocksViewer()
    viewer.show()
    sys.exit(app.exec_())

