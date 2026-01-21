# stock-viewer

Simple stock viewer program.

![logo](https://raw.githubusercontent.com/trucomanx/StockViewer/main/screenshot.png)

## 1. Installing

To install the package from [PyPI](https://pypi.org/project/stock_viewer/), follow the instructions below:


```bash
pip install --upgrade stock_viewer
```

Execute `which stock-viewer` to see where it was installed, probably in `/home/USERNAME/.local/bin/stock-viewer`.

### Using

To start, use the command below:

```bash
stock-viewer
```

The program needs a *.stocks.json file in this format:

```
{
    "KLBN4.SA": {
        "average_price": 4.16,
        "quantity": 9,
        "category": [
            "Sales"
        ]
    },
    "ALUP4.SA": {
        "average_price": 9.42,
        "quantity": 8,
        "category": [
            "Finance"
        ]
    },
    "CPFE3.SA": {
        "average_price": 30.25,
        "quantity": 10,
        "category": [
            "Energy"
        ]
    }
}
```

## 2. More information

If you want more information go to [doc](https://github.com/trucomanx/StockViewer/blob/main/doc) directory.

## 3. Buy me a coffee

If you find this tool useful and would like to support its development, you can buy me a coffee!  
Your donations help keep the project running and improve future updates.  

[☕ Buy me a coffee](https://ko-fi.com/trucomanx) 

## 4. License

This project is licensed under the GPL license. See the `LICENSE` file for more details.
