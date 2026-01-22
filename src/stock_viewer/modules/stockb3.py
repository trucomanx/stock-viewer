import requests
import zipfile
import io
from datetime import datetime, timedelta
import os
from PyQt5.QtWidgets import QApplication

def remove_sa_suffix(ticker: str) -> str:
    ticker = ticker.strip()
    if ticker.upper().endswith(".SA"):
        return ticker[:-3]
    return ticker


class B3History:
    def __init__(self, years_back=2, cache_dir="b3_cache", func_progress100=None):
        self.years_back = years_back
        self.cache_dir = cache_dir
        self.func_progress100 = func_progress100
        os.makedirs(cache_dir, exist_ok=True)

        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=370 * years_back)

        # anos necessários (ex: jan/2026 → 2024, 2025, 2026)
        self.years = list(range(self.start_date.year, self.end_date.year + 1))

        # dataset global carregado UMA VEZ
        self.raw_data = self._load_all_years()

    # ==========================
    # DOWNLOAD GLOBAL (1x)
    # ==========================
    def _download_year_raw(self, year: int) -> list[str]:
        cache_file = os.path.join(self.cache_dir, f"COTAHIST_{year}.txt")

        # cache local bruto
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="latin1") as f:
                return f.read().splitlines()

        print(f"Baixando COTAHIST {year}...")

        url = f"https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP"
        r = requests.get(url)
        r.raise_for_status()
        QApplication.processEvents()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            file_name = z.namelist()[0]
            with z.open(file_name) as f:
                raw = f.read().decode("latin1").splitlines()

        QApplication.processEvents()
        
        # salva cache
        with open(cache_file, "w", encoding="latin1") as f:
            f.write("\n".join(raw))

        QApplication.processEvents()
        
        return raw

    def _load_all_years(self) -> list[str]:
        all_lines = []
        K = len(self.years)

        for k, year in enumerate(self.years):
            all_lines.extend(self._download_year_raw(year))

            if self.func_progress100 is not None:
                self.func_progress100((k + 1) * 100.0 / K)
                QApplication.processEvents()
            
        return all_lines

    # ==========================
    # CONSULTA (SEM DOWNLOAD)
    # ==========================
    def get_prices(self, ticker: str, months: int = 24) -> list[float]:
        ticker = remove_sa_suffix(ticker.upper().strip())

        end_date = self.end_date
        start_date = end_date - timedelta(days=int(30.41 * months)) # months of 30.41 days

        all_data = []
        K = len(self.raw_data)

        if K == 0:
            return []

        STEPS = max(1, K // 100)
        
        for k, line in enumerate(self.raw_data):
            if not line.startswith("01"):
                continue

            try:
                code = line[12:24].strip()
                date = datetime.strptime(line[2:10], "%Y%m%d")
                close_price = int(line[108:121]) / 100
            except:
                continue

            if code == ticker and start_date <= date <= end_date:
                all_data.append((date, close_price))

            if self.func_progress100 is not None and k % STEPS == 0:
                self.func_progress100((k + 1) * 100.0 / K)

        all_data.sort(key=lambda x: x[0])

        if self.func_progress100 is not None:
            self.func_progress100(100.0)
        
        return [price for _, price in all_data]

if __name__ == "__main__":
    def progress(val):
        print(val)

    b3 = B3History(years_back=2, cache_dir="b3_cache", func_progress100=progress) 

    ticker = remove_sa_suffix("BSOX39.SA")

    prices = b3.get_prices(ticker, months=24) 

    print(ticker)
    print(len(prices))
    print(prices)

