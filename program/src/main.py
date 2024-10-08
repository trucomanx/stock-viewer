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

class StocksViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stocks Viewer')
        self.setGeometry(100, 100, 1000, 600)

        self.stocks_data = {}
        self.groups_data = {}
        self.config_data = {}

        self.initUI()
        self.load_default_config()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.table_tab = QWidget()
        self.config_tab = QWidget()

        self.tab_widget.addTab(self.table_tab, 'Visualização de Dados')
        self.tab_widget.addTab(self.config_tab, 'Configurações')

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
        self.stocks_path_edit.setPlaceholderText('Selecione o arquivo *.stocks.json')
        self.stocks_path_edit.setToolTip('Caminho do arquivo stocks.json que contém os dados das ações')
        stocks_layout.addWidget(self.stocks_path_edit)

        self.stocks_button = QPushButton('Selecionar stocks.json', self)
        self.stocks_button.setToolTip('Clique para selecionar o arquivo *.stocks.json')
        self.stocks_button.clicked.connect(self.select_stocks_file)
        stocks_layout.addWidget(self.stocks_button)

        layout.addLayout(stocks_layout)

        # Layout horizontal para groups.json
        groups_layout = QHBoxLayout()
        self.groups_path_edit = QLineEdit(self)
        self.groups_path_edit.setPlaceholderText('Selecione o arquivo *.groups.json')
        self.groups_path_edit.setToolTip('Caminho do arquivo groups.json que contém os grupos de ações')
        groups_layout.addWidget(self.groups_path_edit)

        self.groups_button = QPushButton('Selecionar groups.json', self)
        self.groups_button.setToolTip('Clique para selecionar o arquivo *.groups.json')
        self.groups_button.clicked.connect(self.select_groups_file)
        groups_layout.addWidget(self.groups_button)

        layout.addLayout(groups_layout)

        # Botão de Atualizar
        self.update_button = QPushButton('Atualizar', self)
        self.update_button.setToolTip('Clique para atualizar os dados dos arquivos selecionados')
        self.update_button.clicked.connect(self.update_data)
        layout.addWidget(self.update_button)

        # Botão de Salvar
        self.save_button = QPushButton('Salvar', self)
        self.save_button.setToolTip('Clique para salvar as modificações feitas nos dados das ações')
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(self.save_button)

        # Label
        self.label = QLabel('Selecione um grupo de ações:')
        layout.addWidget(self.label)

        # ComboBox para selecionar o grupo
        self.comboBox = QComboBox()
        self.comboBox.setToolTip('Escolha um grupo de ações para visualizar seus detalhes')
        self.comboBox.currentTextChanged.connect(self.display_table)
        layout.addWidget(self.comboBox)

        # Tabela para mostrar os stocks
        self.tableWidget = QTableWidget()
        self.tableWidget.setToolTip('Tabela que exibe as ações, preços médios, quantidades e montantes totais do grupo selecionado')
        self.tableWidget.itemChanged.connect(self.update_amount)
        layout.addWidget(self.tableWidget)

        # Label para mostrar o montante total do grupo
        self.total_label = QLabel('Montante Total do Grupo: ')
        self.total_label.setToolTip('Mostra o montante total investido no grupo de ações selecionado')
        layout.addWidget(self.total_label)

        self.table_tab.setLayout(layout)

    def setup_config_tab(self):
        layout = QFormLayout()

        # Layout horizontal para config.json
        self.config_path_edit = QLineEdit(self)
        self.config_path_edit.setPlaceholderText('Selecione o arquivo *.stock-viewer.conf.json')
        self.config_path_edit.setToolTip('Caminho do arquivo stock-viewer.conf.json que contém a configuração das colunas')
        layout.addRow('Arquivo de Configuração:', self.config_path_edit)

        self.config_button = QPushButton('Selecionar Configuração', self)
        self.config_button.setToolTip('Clique para selecionar o arquivo *.stock-viewer.conf.json')
        self.config_button.clicked.connect(self.select_config_file)
        layout.addRow('', self.config_button)

        # Botão de Atualizar Configuração
        self.update_config_button = QPushButton('Atualizar Configuração', self)
        self.update_config_button.setToolTip('Clique para atualizar a configuração das colunas na tabela')
        self.update_config_button.clicked.connect(self.update_table_columns)
        layout.addRow('', self.update_config_button)

        self.config_tab.setLayout(layout)

    def select_stocks_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecione o arquivo stocks.json', '', 'Stocks JSON Files (*.stocks.json)')
        if path:
            self.stocks_path_edit.setText(path)

    def select_groups_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecione o arquivo groups.json', '', 'Groups JSON Files (*.groups.json)')
        if path:
            self.groups_path_edit.setText(path)

    def select_config_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecione o arquivo stock-viewer.conf.json', '', 'Config JSON Files (*.stock-viewer.conf.json)')
        if path:
            self.config_path_edit.setText(path)

    def load_default_config(self):
        default_config_path = 'base.stock-viewer.conf.json'
        try:
            with open(default_config_path, 'r') as file:
                self.config_data = json.load(file)
            self.config_path_edit.setText(default_config_path)
        except FileNotFoundError:
            print(f"Arquivo de configuração padrão {default_config_path} não encontrado.")
        except json.JSONDecodeError:
            print(f"Erro ao ler o arquivo de configuração padrão {default_config_path}.")

    def update_data(self):
        stocks_path = self.stocks_path_edit.text()
        groups_path = self.groups_path_edit.text()

        if stocks_path:
            self.stocks_data = self.load_json(stocks_path)

        if groups_path:
            self.groups_data = self.load_json(groups_path)

        self.populate_groups()
        self.update_current_prices()

    def update_table_columns(self):
        config_path = self.config_path_edit.text()

        if not config_path:
            return

        self.config_data = self.load_json(config_path)
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
            stock_name = self.tableWidget.item(row, self.config_data.get('columns', []).index('Stock')).text()
            preco_medio = float(self.tableWidget.item(row, self.config_data.get('columns', []).index('Preço Médio')).text())
            quantidade = int(self.tableWidget.item(row, self.config_data.get('columns', []).index('Quantidade')).text())

            self.stocks_data[stock_name] = {
                'preco_medio': preco_medio,
                'quantidade': quantidade
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
        column_names = self.config_data.get('columns', ['Stock', 'Preço Médio', 'Quantidade', 'Montante Total', 'Preço Atual'])
        self.tableWidget.setColumnCount(len(column_names))
        self.tableWidget.setHorizontalHeaderLabels(column_names)

        self.tableWidget.setRowCount(len(group_stocks))

        for row, stock in enumerate(group_stocks):
            stock_data = self.stocks_data.get(stock, {})
            preco_medio = stock_data.get('preco_medio', 0)
            quantidade = stock_data.get('quantidade', 0)
            montante_total = preco_medio * quantidade

            for col, column in enumerate(column_names):
                if column == 'Stock':
                    item = QTableWidgetItem(stock)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                elif column == 'Preço Médio':
                    item = QTableWidgetItem(f'{preco_medio:.2f}')
                elif column == 'Quantidade':
                    item = QTableWidgetItem(f'{quantidade}')
                elif column == 'Montante Total':
                    item = QTableWidgetItem(f'{montante_total:.2f}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                elif column == 'Preço Atual':
                    item = QTableWidgetItem('')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                else:
                    item = QTableWidgetItem('')

                # Define a cor de fundo para as células não editáveis
                if not (item.flags() & Qt.ItemIsEditable):
                    item.setBackground(QColor('lightgray'))

                self.tableWidget.setItem(row, col, item)

            # Atualizar o montante total do grupo
            total_group_amount += montante_total

        self.total_label.setText(f'Montante Total do Grupo: {total_group_amount:.2f}')
        self.update_current_prices()



    def update_current_prices(self):
        for row in range(self.tableWidget.rowCount()):
            price_current_item = self.tableWidget.item(row, self.config_data.get('columns', []).index('Preço Atual'))  # Coluna 'Preço Atual'
            price_mean_item = self.tableWidget.item(row, self.config_data.get('columns', []).index('Preço Médio'))  # Coluna 'Preço Médio'
            if price_current_item and price_mean_item:
                stock_name = self.tableWidget.item(row, self.config_data.get('columns', []).index('Stock')).text()
                current_price = self.fetch_current_price(stock_name)
                price_current_item.setText(f'{current_price:.2f}')

                # Atualiza a cor da célula com base no preço
                price_mean = float(price_mean_item.text())
                if current_price > price_mean:
                    price_current_item.setBackground(QColor('green'))
                else:
                    price_current_item.setBackground(QColor('red'))

    def fetch_current_price(self, stock_name):
        try:
            stock = yf.Ticker(stock_name)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            return current_price
        except Exception as e:
            print(f"Erro ao obter o preço atual para {stock_name}: {e}")
            return 0.0

    def update_amount(self, item):
        if item.column() in (2, 3):  # Apenas colunas de quantidade e preço médio
            row = item.row()

            preco_medio_item = self.tableWidget.item(row, self.config_data.get('columns', []).index('Preço Médio'))
            quantidade_item = self.tableWidget.item(row, self.config_data.get('columns', []).index('Quantidade'))

            if preco_medio_item and quantidade_item:
                try:
                    quantidade = int(quantidade_item.text())
                    preco_medio = float(preco_medio_item.text())
                    montante_total = quantidade * preco_medio

                    montante_total_item = self.tableWidget.item(row, self.config_data.get('columns', []).index('Montante Total'))
                    if montante_total_item:
                        montante_total_item.setText(f'{montante_total:.2f}')

                    self.update_current_prices()
                except ValueError:
                    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = StocksViewer()
    viewer.show()
    sys.exit(app.exec_())

