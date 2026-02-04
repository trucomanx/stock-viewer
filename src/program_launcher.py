#!/usr/bin/python3

'''
python3 -m venv venv-stock-viewer
source venv-stock-viewer/bin/activate

pip install --upgrade pip
pip install pyinstaller pyinstaller-hooks-contrib
pip install -r requirements.txt
cd src

## windows ##
python3 -m PyInstaller --onefile --windowed --name stock_viewer --add-data "stock_viewer/icons;icons" --collect-all PyQt5 program_launcher.py

## ubuntu ##
python3 -m PyInstaller --onefile --windowed --name stock_viewer --add-data "stock_viewer/icons:icons" --collect-all PyQt5 program_launcher.py

'''

from stock_viewer.prog_viewer import main

if __name__ == "__main__":
    main()

