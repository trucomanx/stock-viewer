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

DEFAULT_CONFIG_PATH='base.stock-viewer.conf.json'

def dicts_to_keys_titles(lista):
    list_keys=[];
    list_titles=[];
    for d in lista:
        list_keys.append(d['key'])
        list_titles.append(d['title'])
    return list_keys,list_titles
        

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

        self.column_keys, self.column_titles = dicts_to_keys_titles(self.config_data["columns"])


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
        self.tableWidget.itemChanged.connect(self.update_amount)
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

        self.populate_groups()
        self.update_currentPrices()

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

        # Atualiza os dados do dicionário `self.stocks_data` com os valores da tabela
        for row in range(self.tableWidget.rowCount()):
            
            stock_name    = self.tableWidget.item(row, self.column_keys.index('stock')).text()
            average_price = float(self.tableWidget.item(row, self.column_keys.index('average_price')).text())
            quantity      = int(self.tableWidget.item(row, self.column_keys.index('quantity')).text())

            self.stocks_data[stock_name] = {
                'average_price': average_price,
                'quantity': quantity
            }

        # Salva os dados atualizados de volta no arquivo JSON
        with open(stocks_path, 'w') as file:
            json.dump(self.stocks_data, file, indent=4)

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

        self.tableWidget.setRowCount(len(group_stocks))

        for row, stock in enumerate(group_stocks):
            stock_data = self.stocks_data.get(stock, {})
            average_price = stock_data.get('average_price', 0)
            quantity = stock_data.get('quantity', 0)
            total_amount = average_price * quantity
            
            for col, column in enumerate(self.column_keys):
                if column == "stock":
                    item = QTableWidgetItem(stock)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                elif column == "average_price":
                    item = QTableWidgetItem(f'{average_price:.2f}')
                elif column == "quantity":
                    item = QTableWidgetItem(f'{quantity}')
                elif column == "total_amount":
                    item = QTableWidgetItem(f'{total_amount:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                elif column == "currentPrice":
                    item = QTableWidgetItem('')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                else:
                    item = QTableWidgetItem('')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável

                # Define a cor de fundo para as células não editáveis
                if not (item.flags() & Qt.ItemIsEditable):
                    item.setBackground(QColor('lightgray'))

                self.tableWidget.setItem(row, col, item)

            # Atualizar o montante total do grupo
            total_group_amount += total_amount

        self.total_label.setText(f'Montante Total do Grupo: {total_group_amount:.2f}')
        self.update_currentPrices()



    def update_currentPrices(self):
        for row in range(self.tableWidget.rowCount()):
            price_current_item = self.tableWidget.item(row, self.column_keys.index('currentPrice'))  # Coluna 'Preço Atual'
            price_mean_item    = self.tableWidget.item(row, self.column_keys.index('average_price'))  # Coluna 'Preço Médio'
            if price_current_item and price_mean_item:
                stock_name = self.tableWidget.item(row, self.column_keys.index('stock')).text()
                currentPrice = self.fetch_currentPrice(stock_name)
                price_current_item.setText(f'{currentPrice:.2f}')

                # Atualiza a cor da célula com base no preço
                price_mean = float(price_mean_item.text())
                if currentPrice > price_mean:
                    price_current_item.setBackground(QColor('green'))
                else:
                    price_current_item.setBackground(QColor('red'))

    def fetch_currentPrice(self, stock_name):
        try:
            stock = yf.Ticker(stock_name)
            currentPrice = stock.history(period='1d')['Close'].iloc[-1]
            return currentPrice
        except Exception as e:
            print(f"Erro ao obter o preço atual para {stock_name}: {e}")
            return 0.0

    def update_amount(self, item):
        if item.column() in (2, 3):  # Apenas colunas de quantity e preço médio
            row = item.row()

            average_price_item = self.tableWidget.item(row, self.column_keys.index('average_price'))
            quantity_item = self.tableWidget.item(row, self.column_keys.index('quantity'))

            if average_price_item and quantity_item:
                try:
                    quantity = int(quantity_item.text())
                    average_price = float(average_price_item.text())
                    total_amount = quantity * average_price

                    total_amount_item = self.tableWidget.item(row, self.column_keys.index('total_amount'))
                    if total_amount_item:
                        total_amount_item.setText(f'{total_amount:.2f}')

                    self.update_currentPrices()
                except ValueError:
                    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = StocksViewer()
    viewer.show()
    sys.exit(app.exec_())

