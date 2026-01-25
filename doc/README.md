# Documentation

* [Install the program](INSTALL.md)
* [Configure the program](CONFIGURE.md)
* [Upload to PYPI](UPLOAD.md)
* [Testing from source](TESTING.md)

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
