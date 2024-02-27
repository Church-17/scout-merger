from urllib.parse import quote as url_encode
from requests import get as request
from pandas import read_csv, DataFrame

class GoogleSheet:
    def __init__(self, spreadsheet_url):
        self.url = spreadsheet_url

    def read(self, sheet_name: str) -> DataFrame:
        return read_csv(f"{self.url}/gviz/tq?tqx=out:csv&sheet={url_encode(sheet_name)}")

    def download(self, download_path: str):
        response = request(f"{self.url}/export?mimeType=application%2Fvnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with open(download_path, 'wb') as file:
            file.write(response.content)
