#!/usr/bin/python3

import os
import sys
import json
import signal

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QTableWidget, QProgressBar, 
    QTableWidgetItem, QWidget, QPushButton, QLineEdit, QFileDialog, QHBoxLayout, 
    QTabWidget, QFormLayout, QSplitter, QMenu, QSizePolicy
)

from PyQt5.QtGui  import QColor, QIcon, QFont, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer

import pyqtgraph as pg
import numpy as np
import math

from stock_viewer.modules.stock       import agregate_more_stock_info
from stock_viewer.modules.text_editor import open_with_default_text_editor
from stock_viewer.modules.categorize  import categorize_stocks
from stock_viewer.modules.wabout      import show_about_window

from stock_viewer.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu

import stock_viewer.about as about
import stock_viewer.modules.configure as configure 


DEFAULT_TABLE_CONFIG_PATH = os.path.join(   os.path.expanduser("~"),
                                            ".config",
                                            about.__package__,
                                            "default."+about.__program_name__+".table.json")


PROGRAM_CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                                    ".config",
                                    about.__package__,
                                    about.__program_name__+".conf.json")

DEFAULT_TABLE_CONTENT={
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
        {"key":"daysData2y",         "title":"2y",             "tooltip":"Two years"},
        {"key":"daysData6mo",        "title":"6mo",            "tooltip":"Six months"},
        {"key":"daysData1mo",        "title":"1mo",            "tooltip":"One month"},
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

DEFAULT_PROGRAM_CONTENT={ 
    "button_groupplot": "G. plot",
    "button_groupplot_tooltip": "Plot of amount by group",
    "button_prog_configure": "Settings",
    "button_prog_configure_tooltip": "Open the configure Json file of program",  
    "button_update": "To update",
    "button_update_tooltip": "To update in the program the quantities and average prices from a JSON file.",
    "button_save": "Save",
    "button_save_tooltip": "Save the quantity and average prices in a JSON file",
    "button_coffee": "Coffee",
    "button_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "button_about": "About",
    "button_about_tooltip": "About the program",
    "toolbutton_icon_size": 32,
    "window_width": 1200,
    "window_height": 800,
    "data_visualization": "Data Visualization",
    "table_settings": "Table settings",
    "stocks_path_edit": "Select *.stocks.json",
    "stocks_path_edit_tooltip": "Path to the stocks.json file that contains the stock data",
    "stocks_button": "Select *.stocks.json",
    "stocks_button_tooltip": "Click to select the *.stocks.json file",
    "update_button": "To update",
    "update_button_tooltip": "Click to update data for selected files",
    "select_group": "Select a group:",
    "select_group_tooltip": "Choose a stock group to view its details",
    "table_tooltip": "Table displaying the shares, average prices, quantities and total amounts of the selected group",
    "total_amount": "Total amount/gain of group: ",
    "total_amount_tooltip": "Shows the total amount invested in the selected stock group",
    "config_path_edit": "Select the *.stock-viewer.table.json file",
    "config_path_edit_tooltip": "Path to the stock-viewer.table.json file that contains the columns configuration",
    "config_path_edit_label": "Configuration File:",
    "config_button": "Select Configuration",
    "config_button_tooltip": "Click to select the *.stock-viewer.table.json file",
    "config_edit_button": "Edit configuration file",
    "config_edit_button_tooltip": "Click to open the *.stock-viewer.table.json file",
    "update_config_button": "Update Configuration",
    "update_config_button_tooltip": "Click to update the column configuration in the table",
    "select_stocks_json_file": "Select the *.stocks.json file",
    "select_stocks_json_file_filter": "Stocks JSON Files (*.stocks.json)",
    "select_table_json_file": "Select the *.stock-viewer.table.json file",
    "select_table_json_file_filter": "Config JSON Files (*.stock-viewer.table.json)",
    "green_color": "#d3ffc7",
    "red_color": "#ffc9d6",
    "search_yahoo": "Search Yahoo finance",
    "search_google": "Search Google",
    "copy_cell": "Copy cell", 
    "plot_color": "blue", 
    "plot_linewidth": 2,
    "plot_bgcolor": "white", 
    "plot_pccolor": "red", 
    "plot_xlabel": "Working days",
    "plot_ylabel": "Price",
    "plot_ylabel2": "Variation"
}

configure.verify_default_config(DEFAULT_TABLE_CONFIG_PATH, default_content=DEFAULT_TABLE_CONTENT)
configure.verify_default_config(PROGRAM_CONFIG_PATH      , default_content=DEFAULT_PROGRAM_CONTENT)

CONFIG=configure.load_config(PROGRAM_CONFIG_PATH)

def show_bar_plot_hor(labels, values, title="", color = "blue"):
    w = pg.plot()
    w.setWindowTitle(title)

    # FUNDO branco TOTAL
    w.setBackground("w")
    w.getViewBox().setBackgroundColor("w")

    y = list(range(len(labels)))

    x_max = max(values)
    x_min = 0 # min(values)

    # ==== GRID MANUAL (ATRÁS) ====
    pct = 0.10
    x_ext_max = np.ceil(x_max * (1.0 + pct))

    
    step = (x_ext_max-x_min)/5
    def floor_one_sig_digit(n):
        if n == 0:
            return 0
        power = np.floor(np.log10(abs(n)))
        factor = 10 ** power
        return np.floor(n / factor) * factor
    step_round = floor_one_sig_digit(step)
    x_min_round = floor_one_sig_digit(x_min)
    x_max_round = floor_one_sig_digit(x_max)

    for x in np.arange(x_min_round, x_max_round+2*step_round, step_round):
        line = pg.InfiniteLine(
            pos=x,
            angle=90,
            pen=pg.mkPen((200, 200, 200), width=1)
        )
        line.setZValue(-100)
        w.addItem(line)

    # ==== BARRAS HORIZONTAIS ====
    bars = pg.BarGraphItem(
        x0=[0] * len(values),
        x1=values,
        y=y,
        height=0.7,
        brush=color
    )
    bars.setZValue(10)
    w.addItem(bars)

    # ==== LABELS eixo Y ====
    axis = w.getAxis("left")
    axis.setTicks([list(zip(y, labels))])

    # ==== TEXTO DOS VALORES (lado direito da barra) ====
    offset = x_max * 0.01  # espaçamento visual
    for yi, val in zip(y, values):
        if val>1000:
            val_text = f"{val/1000:.3f} k"
        else:
            val_text = f"{val:.2f}"
        txt = pg.TextItem(
            text=val_text,
            anchor=(0, 0.5),   # alinhado à esquerda, centrado vertical
            color=color
        )
        
        font = QFont()
        font.setBold(True)
        #font.setPointSize(10)  # opcional

        txt.setPos(val + offset, yi)
        txt.setZValue(20)
        w.addItem(txt)

    # ==== LIMITES ====
    w.setYRange(-0.6, len(labels) - 0.4)
    w.setXRange(x_min, x_max * 1.12)  # extra espaço p/ texto

    # ==== MARGENS ====
    w.getPlotItem().layout.setContentsMargins(20, 20, 20, 20)

    w.resize(900, 520)

    w.show()
    return w



def plot_1d_simple_widget(prices,color="red", width=1):
    w = pg.PlotWidget()
    time=list(range(len(prices)));
    w.plot(
        time, 
        prices,
        pen=pg.mkPen(color=color, width=width)
    )
    
    w.hideAxis('bottom')
    w.hideAxis('left')
    
    return w

class PercentAxis(pg.AxisItem):
    def __init__(self, average_price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.avg = average_price

    def tickStrings(self, values, scale, spacing):
        return [
            f"{(v / self.avg - 1) * 100:+.1f}%"
            for v in values
        ]


def plot_1d_complex(
    prices,
    average_price,
    color="red",
    width=2,
    bgcolor="white",
    pccolor="red",
    xlabel="Working days",
    ylabel="Price",
    ylabel2="Variation",
    enable_crosshair=True,   # 👈 parâmetro novo
):

    if not prices:
        return pg.PlotWidget()

    n = len(prices)
    x = list(range(-n + 1, 1))
    y = prices

    # eixo direito percentual
    right_axis = PercentAxis(average_price, orientation='right')

    w = pg.PlotWidget(axisItems={'right': right_axis})
    w.setBackground(bgcolor)
    w.showAxis('right')

    plot_item = w.getPlotItem()
    vb = plot_item.getViewBox()

    # curva
    plot_item.plot(
        x,
        y,
        pen=pg.mkPen(color=color, width=width),
        antialias=True
    )

    # linha média
    avg_line = pg.InfiniteLine(
        pos=average_price,
        angle=0,
        pen=pg.mkPen(pccolor, width=width, style=Qt.DashLine)
    )
    plot_item.addItem(avg_line)

    # --------------------------------------------------
    # RANGE FIXO (evita pulo ao redimensionar)
    # --------------------------------------------------
    ymin = min(y)
    ymax = max(y)
    
    ymin = min([average_price, ymin])
    ymax = max([average_price, ymax])

    padding = (ymax - ymin) * 0.05 or 1.0
    vb.setYRange(ymin - padding, ymax + padding, padding=0)

    # 🔒 TRAVA O AUTORANGE (ESSENCIAL)
    vb.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
    vb.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)

    # --------------------------------------------------
    # CONFIGURAÇÃO DO EIXO X COM 13 TICKS
    # --------------------------------------------------
    import numpy as np
    x_ticks = np.linspace(x[0], x[-1], 13)  # 13 ticks -> 12 partes
    x_labels = [(pos, f"{int(pos)}") for pos in x_ticks]
    plot_item.getAxis('bottom').setTicks([x_labels])

    # labels e grid
    plot_item.setLabel('left', ylabel)
    plot_item.setLabel('right', ylabel2)
    plot_item.setLabel('bottom', xlabel)

    plot_item.showGrid(x=True, y=True, alpha=0.3)
    vb.setDefaultPadding(0.05)

    # --------------------------------------------------
    # CROSSHAIR + MOUSE (opcional)
    # --------------------------------------------------
    vline = None
    label = None

    if enable_crosshair:
        vline = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen('gray', style=Qt.DashLine)
        )
        plot_item.addItem(vline, ignoreBounds=True)

        label = pg.TextItem("", anchor=(0, 1), color=color)
        plot_item.addItem(label)
        

        def mouse_moved(evt):
            # proteção contra ViewBox inválido
            if vb.width() < 20 or vb.height() < 20:
                return

            #vr = vb.viewRect()
            #print(vr.width(),vr.height())
           
            pos = evt[0]
            if not plot_item.sceneBoundingRect().contains(pos):
                return

            mouse_point = vb.mapSceneToView(pos)
            x_mouse = mouse_point.x()
            y_mouse = mouse_point.y()

            idx = int(round(x_mouse - x[0]))
            if 0 <= idx < len(x):
                y_plot = y[idx]

                vline.setPos(x[idx])
                label.setText(
                    f"x: {x[idx]}\n"
                    f"{ylabel}: {y_plot:.2f}"
                )
                label.setPos(x[idx], y_mouse)

        # manter referência viva
        w._mouse_proxy = pg.SignalProxy(
            w.scene().sigMouseMoved,
            rateLimit=60,
            slot=mouse_moved
        )

    
    return w



def day_data_color_and_percent(prices, green_color="green", red_color="red"):
    if len(prices)==0:
        return "white", 0.0

    percent = (prices[-1] - prices[0])*100.0/prices[0]

    if prices[0]<prices[-1]:
        return green_color, percent

    return red_color, percent


def dicts_to_keys_titles(lista):
    list_keys=[];
    list_titles=[];
    list_tooltips=[];
    for d in lista:
        list_keys.append(d['key'])
        list_titles.append(d['title'])
        list_tooltips.append(d['tooltip'])
    return list_keys,list_titles,list_tooltips

# Subclassificando QTableWidgetItem para suportar ordenação numérica, incluindo NaN
class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)  # Chama o construtor da classe base
        # Tenta converter o texto em número para definir o alinhamento
        try:
            float_value = float(text)
            # Se for um número, justifica à direita
            self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        except ValueError:
            # Se não for um número, mantém o alinhamento padrão
            pass

    def __lt__(self, other):
        # Tenta converter os itens em números float
        try:
            value1 = float(self.text())
        except ValueError:
            return super().__lt__(other)  # Se não for número, compara como string
        
        try:
            value2 = float(other.text())
        except ValueError:
            return super().__lt__(other)  # Se não for número, compara como string

        # Verifica se algum valor é NaN e define a lógica de ordenação
        if math.isnan(value1):
            return False  # Coloca NaN no final
        if math.isnan(value2):
            return True  # Coloca NaN no final

        # Compara numericamente se ambos os valores são válidos
        return value1 < value2

        
################################################################################
################################################################################
################################################################################
class StocksViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.setGeometry(0, 0, CONFIG["window_width"], CONFIG["window_height"])

        self.stocks_data = {}
        self.groups_data = {}
        self.config_data = {}
        
        self.plot_windows = []  # manter referência às janelas abertas

        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(self.icon_path)) 

        self.initUI()
        self.config_data=self.load_config_file();

        self.column_keys, self.column_titles, self.column_tooltips = dicts_to_keys_titles(self.config_data["columns"])


    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.table_tab = QWidget()
        self.config_tab = QWidget()

        self.tab_widget.addTab(self.table_tab , CONFIG["data_visualization"])
        self.tab_widget.addTab(self.config_tab, CONFIG["table_settings"])

        self.setup_table_tab()
        self.setup_config_tab()

        layout.addWidget(self.tab_widget)
        
        # progress bar
        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def setup_table_tab(self):
        layout = QVBoxLayout()

        # Layout horizontal para stocks.json
        stocks_layout = QHBoxLayout()
        
        self.stocks_path_edit = QLineEdit(self)
        self.stocks_path_edit.setPlaceholderText(CONFIG["stocks_path_edit"])
        self.stocks_path_edit.setToolTip(CONFIG["stocks_path_edit_tooltip"])
        stocks_layout.addWidget(self.stocks_path_edit)

        self.stocks_button = QPushButton(CONFIG["stocks_button"], self)
        self.stocks_button.setToolTip(CONFIG["stocks_button_tooltip"])
        self.stocks_button.setIcon(QIcon.fromTheme("document-open"))
        self.stocks_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.stocks_button.clicked.connect(self.select_stocks_file)
        stocks_layout.addWidget(self.stocks_button)

        layout.addLayout(stocks_layout)

        #
        buttons_layout = QHBoxLayout()
        
        # Botão de Atualizar
        self.update_button = QPushButton(CONFIG["update_button"], self)
        self.update_button.setToolTip(CONFIG["update_button_tooltip"])
        self.update_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.update_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.update_button.clicked.connect(self.update_data)
        buttons_layout.addWidget(self.update_button)

        # Botão de Salvar
        self.save_button = QPushButton(CONFIG["button_save"], self)
        self.save_button.setToolTip(CONFIG["button_save_tooltip"])
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.save_button.clicked.connect(self.save_data)
        buttons_layout.addWidget(self.save_button)

        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttons_layout.addWidget(spacer)

        # Group plot
        self.groupplot_button = QPushButton(CONFIG["button_groupplot"], self)
        self.groupplot_button.setToolTip(CONFIG["button_groupplot_tooltip"])
        self.groupplot_button.setIcon(QIcon.fromTheme("applications-graphics"))
        self.groupplot_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.groupplot_button.clicked.connect(self.on_groupplot_click)
        self.groupplot_button.setEnabled(False)
        buttons_layout.addWidget(self.groupplot_button)

        # Configure
        self.configure_button = QPushButton(CONFIG["button_prog_configure"], self)
        self.configure_button.setToolTip(CONFIG["button_prog_configure_tooltip"])
        self.configure_button.setIcon(QIcon.fromTheme("document-properties"))
        self.configure_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.configure_button.clicked.connect(self.on_configure_click)
        buttons_layout.addWidget(self.configure_button)

        # Coffee
        self.coffee_button = QPushButton(CONFIG["button_coffee"], self)
        self.coffee_button.setToolTip(CONFIG["button_coffee_tooltip"])
        self.coffee_button.setIcon(QIcon.fromTheme("emblem-favorite"))
        self.coffee_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.coffee_button.clicked.connect(self.on_coffee_click)
        buttons_layout.addWidget(self.coffee_button)
        
        # About
        self.about_button = QPushButton(CONFIG["button_about"], self)
        self.about_button.setToolTip(CONFIG["button_about_tooltip"])
        self.about_button.setIcon(QIcon.fromTheme("help-about"))
        self.about_button.setIconSize(QSize(CONFIG["toolbutton_icon_size"], CONFIG["toolbutton_icon_size"]))
        self.about_button.clicked.connect(self.about_data)
        buttons_layout.addWidget(self.about_button)

        layout.addLayout(buttons_layout)

        # Label
        self.label = QLabel(CONFIG["select_group"])
        layout.addWidget(self.label)

        # ComboBox para selecionar o grupo
        self.comboBox = QComboBox()
        self.comboBox.setToolTip(CONFIG["select_group_tooltip"])
        self.comboBox.currentTextChanged.connect(self.display_table)
        self.comboBox.setStyleSheet('''
            QComboBox {
                color: #000000;               /* Cor do texto */
                background-color: #DDDDFF;    /* Cor de fundo */
                border: 2px solid #AAAAEE;    /* Borda azul-escuro */
                /*padding: 5px;*/             /* Espaçamento interno */
            }
            QComboBox QAbstractItemView {
                background-color: #DDDDFF;    /* Fundo das opções ao abrir */
                color: #000000;               /* Cor do texto das opções */
                selection-background-color: #0055aa;  /* Fundo do item selecionado */
            }
        ''') # Estiliza o QComboBox
        
        layout.addWidget(self.comboBox)

        # splitter vertical
        self.splitter = QSplitter(Qt.Vertical)

        # Tabela para mostrar os stocks
        self.tableWidget = QTableWidget()
        self.tableWidget.setToolTip(CONFIG["table_tooltip"])
        self.tableWidget.setSortingEnabled(True) # Habilitar a ordenação ao clicar nos títulos das colunas
        self.tableWidget.itemChanged.connect(self.callback_item_changed)
        self.tableWidget.currentCellChanged.connect(self.on_current_cell_changed)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.on_table_context_menu)
        
        # tabela
        self.splitter.addWidget(self.tableWidget)

        # widget inferior (placeholder do gráfico)
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_container.setLayout(self.plot_layout)

        self.splitter.addWidget(self.plot_container)

        # tamanhos iniciais (70% tabela / 30% gráfico)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)

        layout.addWidget(self.splitter)

        # Label para mostrar o montante total do grupo
        self.total_label = QLabel(CONFIG["total_amount"])
        self.total_label.setToolTip(CONFIG["total_amount_tooltip"])
        font = QFont()
        font.setBold(True)
        #font.setPointSize(14)
        self.total_label.setFont(font) # aplica negrito
        self.total_label.setStyleSheet('color: black; background-color: #DDDDFF;') #border: 2px solid black; padding: 5px;
        
        layout.addWidget(self.total_label)
        
        self.table_tab.setLayout(layout)

    def setup_config_tab(self):
        layout = QFormLayout()

        # Layout horizontal para config.json
        self.config_path_edit = QLineEdit(self)
        self.config_path_edit.setPlaceholderText(CONFIG["config_path_edit"])
        self.config_path_edit.setToolTip(CONFIG["config_path_edit_tooltip"])
        self.config_path_edit.setText(DEFAULT_TABLE_CONFIG_PATH)
        layout.addRow(CONFIG["config_path_edit_label"], self.config_path_edit)

        self.config_button = QPushButton(CONFIG["config_button"], self)
        self.config_button.setToolTip(CONFIG["config_button_tooltip"])
        self.config_button.clicked.connect(self.select_config_file)
        layout.addRow('', self.config_button)

        self.config_edit_button = QPushButton(CONFIG["config_edit_button"], self)
        self.config_edit_button.setToolTip(CONFIG["config_edit_button_tooltip"])
        self.config_edit_button.clicked.connect(self.edit_config_file)
        layout.addRow('', self.config_edit_button)

        # Botão de Atualizar Configuração
        self.update_config_button = QPushButton(CONFIG["update_config_button"], self)
        self.update_config_button.setToolTip(CONFIG["update_config_button_tooltip"])
        self.update_config_button.clicked.connect(self.update_table_columns)
        layout.addRow('', self.update_config_button)

        self.config_tab.setLayout(layout)

    def on_groupplot_click(self):
        '''
            self.groups_data = {
                '*': ['ALUP4.SA', 'BBAS3.SA', 'CPLE3.SA', 'DISB34.SA', 'NFLX34.SA'], 
                'Energia': ['ALUP4.SA', 'CPLE3.SA'], 
                'Financiero': ['BBAS3.SA'], 
                'Entretenimento': ['DISB34.SA', 'NFLX34.SA']
            }
        '''
        dict_data = {}
        for group in self.groups_data:
            if group !="*":
                val = 0
                for ticker in self.groups_data[group]:
                    quantity = self.stocks_data[ticker].get('quantity', 0.0) 
                    currentPrice = self.stocks_data[ticker].get('currentPrice', 0.0) 
                    val += quantity * currentPrice
                dict_data[group] = val
        
        labels = list(dict_data.keys())
        values = list(dict_data.values()) 
        
        pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=False)
        labels_sorted, values_sorted = zip(*pairs)
        labels_sorted = list(labels_sorted)
        values_sorted = list(values_sorted)
        
        win = show_bar_plot_hor(labels_sorted, values_sorted, title="")
        self.plot_windows.append(win)  # evita GC fechar a janela
        #print(dict_data)

    def about_data(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)
        
    def on_coffee_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    
    def on_configure_click(self):
        open_with_default_text_editor(PROGRAM_CONFIG_PATH)
        

    def select_stocks_file(self):
        path, _ = QFileDialog.getOpenFileName(  self,
                                                CONFIG["select_stocks_json_file"],
                                                '',
                                                CONFIG["select_stocks_json_file_filter"]
                                            )

        if path:
            self.stocks_path_edit.setText(path)

            # ⏳ deixa o Qt fechar e repintar o diálogo primeiro
            QTimer.singleShot(0, self.update_data)


    def select_config_file(self):
        path, _ = QFileDialog.getOpenFileName(  self, 
                                                CONFIG["select_table_json_file"], 
                                                '', 
                                                CONFIG["select_table_json_file_filter"] )
        if path:
            self.config_path_edit.setText(path)
            self.config_data=self.load_config_file();

    def edit_config_file(self):
        path = self.config_path_edit.text()
        if path:
            open_with_default_text_editor(path)

    def load_config_file(self):
        config_path = self.config_path_edit.text()
        config_data = configure.load_config(config_path)
        
        return config_data;
           
    def update_data(self):
        self.setEnabled(False)

        try:
            stocks_path = self.stocks_path_edit.text()
            if stocks_path:
                self.stocks_data = self.load_json(stocks_path)
                self.groups_data = categorize_stocks(stocks_path)
                self.stocks_data = agregate_more_stock_info(
                    self.stocks_data,
                    progress=self.progress,
                    parent=self
                )

                self.populate_groups()
                self.update_colors_in_table_items()

        finally:
            self.setEnabled(True)
            self.groupplot_button.setEnabled(True)


    def update_table_columns(self):
        self.config_data=self.load_config_file();
        self.column_keys, self.column_titles, self.column_tooltips = dicts_to_keys_titles(self.config_data["columns"])
        
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
            #print("\nInit")

            if len(self.stocks_data[stock_name].get('category',[]))<1:
                dict_to_save[stock_name] = {
                    'average_price': self.stocks_data[stock_name]["average_price"],
                    'quantity':      self.stocks_data[stock_name]["quantity"]
                }
            else:
                #print("\nInit")
                #print(set(self.stocks_data[stock_name]["category"]))
                #print(set(self.stocks_data[stock_name]["category"]).discard("*"))
                #print(list(set(self.stocks_data[stock_name]["category"]).discard("*")))
                
                cats = set(self.stocks_data[stock_name].get("category",[]))
                try:
                    cats = cats.remove("*");
                except:
                    pass;
                
                cats = list(cats)
                
                dict_to_save[stock_name] = {
                    'average_price': self.stocks_data[stock_name]["average_price"],
                    'quantity':      self.stocks_data[stock_name]["quantity"],
                    'category': cats
                }
                #print("End\n")
            #print("End\n")
        
        # Salva os dados atualizados de volta no arquivo JSON
        with open(stocks_path, 'w') as file:
            json.dump(dict_to_save, file, indent=4)

    def populate_groups(self):
        self.comboBox.clear()
        self.comboBox.addItems(sorted(self.groups_data.keys()))
        self.display_table(self.comboBox.currentText())

    def display_table(self, group_name):
        if not group_name or group_name not in self.groups_data:
            return

        self.tableWidget.blockSignals(True)
        self.tableWidget.setSortingEnabled(False)
        
        try: 
            group_stocks = self.groups_data[group_name]
            total_group_amount = 0
            total_group_gain = 0

            # Configuração de colunas
            self.tableWidget.clear()  # Limpa os dados da tabela
            self.tableWidget.setColumnCount(len(self.column_titles))
            self.tableWidget.setHorizontalHeaderLabels(self.column_titles)
            
            # Adicionar os tooltips em todas as colunas
            for i in range(self.tableWidget.columnCount()):
                header_item = self.tableWidget.horizontalHeaderItem(i)  # Obter o item do cabeçalho
                header_item.setToolTip(self.column_tooltips[i])

            self.tableWidget.setRowCount(len(group_stocks))
            
            for row, stock in enumerate(group_stocks):
                stock_data = self.stocks_data.get(stock, {})
                
                value=str(stock)
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
                        
                    elif column == "initial_amount":
                        value = stock_data.get('initial_amount', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "capital_gain":
                        value = stock_data.get('capital_gain', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "capital_gain_ratio":
                        value = stock_data.get('capital_gain_ratio', float("nan")) 
                        item = NumericTableWidgetItem(f'{value*100.0:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "currentPrice":
                        value = stock_data.get('currentPrice', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "longName":
                        value = stock_data.get('longName', '') 
                        item = QTableWidgetItem(f'{value}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável

                    elif column == "daysData2y":
                        prices = stock_data.get('daysData2y',[])
                        color, percent = day_data_color_and_percent(prices)
                        plot = plot_1d_simple_widget(prices, color=color)
                        self.tableWidget.setCellWidget(row, col, plot)
                        # ainda precisa de um item "vazio" para sorting funcionar
                        item = QTableWidgetItem(f'{percent}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "daysData6mo":
                        prices = stock_data.get('daysData6mo',[])
                        color, percent = day_data_color_and_percent(prices)
                        plot = plot_1d_simple_widget(prices, color=color)
                        self.tableWidget.setCellWidget(row, col, plot)
                        # ainda precisa de um item "vazio" para sorting funcionar
                        item = QTableWidgetItem(f'{percent}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "daysData1mo":
                        prices = stock_data.get('daysData1mo',[])
                        color, percent = day_data_color_and_percent(prices)
                        plot = plot_1d_simple_widget(prices, color=color)
                        self.tableWidget.setCellWidget(row, col, plot)
                        # ainda precisa de um item "vazio" para sorting funcionar
                        item = QTableWidgetItem(f'{percent}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "dividendYield":
                        value = stock_data.get('dividendYield', float("nan")) 
                        item = NumericTableWidgetItem(f'{value*1.0:.2f}') # factor
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "fiveYearAvgDividendYield":
                        value = stock_data.get('fiveYearAvgDividendYield', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}') # percentage no factor
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "forwardPE":
                        value = stock_data.get('forwardPE', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "trailingEps":
                        value = stock_data.get('trailingEps', float("nan")) 
                        item = NumericTableWidgetItem(f'{value:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "pegRatio":
                        value = stock_data.get('pegRatio', float("nan")) 
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
                        
                    elif column == "profitMargins":
                        value = stock_data.get('profitMargins', float("nan")) 
                        item = NumericTableWidgetItem(f'{value*100.0:.2f}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "sector":
                        value = stock_data.get('sector', '') 
                        item = QTableWidgetItem(f'{value}')
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Torna a célula não editável
                        
                    elif column == "industry":
                        value = stock_data.get('industry', '') 
                        item = QTableWidgetItem(f'{value}')
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
                total_group_gain   += stock_data.get('capital_gain', 0)

            msg = CONFIG["total_amount"]
            msg+= f'{total_group_amount/1000.0:.3f} K'
            msg+= ' / '
            msg+= f'{total_group_gain/1000.0:.3f} K'
            self.total_label.setText(msg)
            self.update_colors_in_table_items()

        finally:
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.blockSignals(False)


    def update_color_currentPrice(self, row):
        price_current_item = self.tableWidget.item(row, self.column_keys.index('currentPrice'))  # Coluna 'Preço Atual'
        price_mean_item    = self.tableWidget.item(row, self.column_keys.index('average_price'))  # Coluna 'Preço Médio'
        
        if price_current_item and price_mean_item:
            # Atualiza a cor da célula com base no preço
            price_mean   = float(price_mean_item.text())
            currentPrice = float(price_current_item.text())
            
            if currentPrice > price_mean:
                price_current_item.setBackground(QColor(CONFIG["green_color"])) # green
            else:
                price_current_item.setBackground(QColor(CONFIG["red_color"])) # red
    
    def update_color_generic(self,name,row):
        item = self.tableWidget.item(row, self.column_keys.index(name)) 

        if item:
            value  = float(item.text())
    
            if value>0:
                item.setBackground(QColor(CONFIG["green_color"])) # green
            else:
                item.setBackground(QColor(CONFIG["red_color"])) # red
    
    def update_colors_in_table_items(self):
        for row in range(self.tableWidget.rowCount()):
            self.update_color_currentPrice( row)
            self.update_color_generic("capital_gain_ratio",row)
            self.update_color_generic("capital_gain",row)

    def on_current_cell_changed(self, row, column, previous_row, previous_column):
        if row < 0:
            return

        id_stock = self.column_keys.index('stock')
        stock_item = self.tableWidget.item(row, id_stock)

        if not stock_item:
            return

        stock_name = stock_item.text()

        # mostra gráfico 2y no painel inferior
        self.show_stock_plot_2y(stock_name, 
                                color=CONFIG["plot_color"], 
                                width=CONFIG["plot_linewidth"],
                                bgcolor=CONFIG["plot_bgcolor"], 
                                pccolor=CONFIG["plot_pccolor"], 
                                xlabel=CONFIG["plot_xlabel"],
                                ylabel=CONFIG["plot_ylabel"],
                                ylabel2=CONFIG["plot_ylabel2"] )


    def show_stock_plot_2y( self, 
                            stock_name, 
                            color="blue", 
                            width=2,
                            bgcolor="white", 
                            pccolor="red", 
                            xlabel="Working days",
                            ylabel="Price",
                            ylabel2="Variation" ):
        # limpa gráfico anterior
        while self.plot_layout.count():
            item = self.plot_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        stock_data = self.stocks_data.get(stock_name)
        if not stock_data:
            return

        prices = stock_data.get('daysData2y', [])
        average_price = stock_data.get('average_price', None)

        if not prices or average_price is None:
            return

        plot = plot_1d_complex(
            prices,
            average_price,
            color=color,
            width=width,
            bgcolor=bgcolor, 
            pccolor=pccolor, 
            xlabel=xlabel,
            ylabel=ylabel,
            ylabel2=ylabel2
        )
        plot.setTitle("2y - "+stock_name)

        self.plot_layout.addWidget(plot)

    def on_table_context_menu(self, pos):
        # índice lógico (row / column)
        index = self.tableWidget.indexAt(pos)
        if not index.isValid():
            return

        row    = index.row()
        column = index.column()

        item = self.tableWidget.item(row, column)
        if not item:
            return

        cell_text = item.text()

        # nome do stock (sempre da coluna 'stock')
        id_stock   = self.column_keys.index('stock')
        stock_item = self.tableWidget.item(row, id_stock)
        stock_name = stock_item.text() if stock_item else ""

        menu = QMenu(self.tableWidget)

        # --- Copy ---
        action_copy = menu.addAction(CONFIG["copy_cell"])
        action_copy.triggered.connect(
            lambda: QApplication.clipboard().setText(cell_text)
        )

        # --- Search Google ---
        if stock_name:
            action_search = menu.addAction(CONFIG["search_google"]+f": {stock_name}")
            action_search.triggered.connect(
                lambda: QDesktopServices.openUrl(
                    QUrl(f"https://www.google.com/search?q={stock_name}")
                )
            )
            
        # --- Search Yahoo ---
        if stock_name:
            action_search = menu.addAction(CONFIG["search_yahoo"]+f": {stock_name}")
            action_search.triggered.connect(
                lambda: QDesktopServices.openUrl(
                    QUrl(f"https://finance.yahoo.com/quote/{stock_name}/")
                )
            )
        
        # mostra o menu na posição correta
        global_pos = self.tableWidget.viewport().mapToGlobal(pos)
        menu.exec_(global_pos)


    def callback_item_changed(self, item):
        # Proteção global
        self.tableWidget.blockSignals(True)
        self.tableWidget.setSortingEnabled(False)

        try:
            id_stock = self.column_keys.index('stock')
            id_avr   = self.column_keys.index('average_price')
            id_qtty  = self.column_keys.index('quantity')

            col = item.column()
            row = item.row()

            # Só reage a quantity e average_price
            if col not in (id_qtty, id_avr):
                return

            stock_item = self.tableWidget.item(row, id_stock)
            if not stock_item:
                return

            stock_name = stock_item.text()

            average_price_item = self.tableWidget.item(row, id_avr)
            quantity_item      = self.tableWidget.item(row, id_qtty)

            try:
                average_price = float(average_price_item.text()) if average_price_item else 0.0
            except ValueError:
                average_price = 0.0

            try:
                quantity = int(quantity_item.text()) if quantity_item else 0
            except ValueError:
                quantity = 0

            # --- Atualiza stocks_data ---
            if col == id_avr:
                self.stocks_data[stock_name]["average_price"] = average_price
                self.update_color_currentPrice(row)

            if col == id_qtty:
                self.stocks_data[stock_name]["quantity"] = quantity

            # --- Cálculos ---
            initial_amount = quantity * average_price
            total_amount   = quantity * self.stocks_data[stock_name]["currentPrice"]

            self.stocks_data[stock_name]["total_amount"] = total_amount

            # total_amount
            col_total_amount = self.column_keys.index('total_amount')
            item_total = self.tableWidget.item(row, col_total_amount)
            if item_total:
                item_total.setText(f"{total_amount:.2f}")

            # initial_amount
            col_initial_amount = self.column_keys.index('initial_amount')
            item_initial = self.tableWidget.item(row, col_initial_amount)
            if item_initial:
                item_initial.setText(f"{initial_amount:.2f}")

            # capital_gain
            col_capital_gain = self.column_keys.index('capital_gain')
            item_gain = self.tableWidget.item(row, col_capital_gain)
            if item_gain:
                gain = total_amount - initial_amount
                item_gain.setText(f"{gain:.2f}")
                self.update_color_generic("capital_gain", row)

            # capital_gain_ratio
            col_ratio = self.column_keys.index('capital_gain_ratio')
            item_ratio = self.tableWidget.item(row, col_ratio)
            if item_ratio:
                ratio = 0.0
                if initial_amount != 0:
                    ratio = (total_amount - initial_amount) * 100.0 / initial_amount
                item_ratio.setText(f"{ratio:.2f}")
                self.update_color_generic("capital_gain_ratio", row)

        finally:
            # 🔐 GARANTIA ABSOLUTA de restauração
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.blockSignals(False)



# -------------------------------
# Main
# -------------------------------
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"))
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), overwrite=True)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    
    viewer = StocksViewer()
    viewer.show()
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    main()

