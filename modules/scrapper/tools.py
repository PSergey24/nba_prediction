import requests
from bs4 import BeautifulSoup


class BSTools:

    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url)
        return BeautifulSoup(response.text, "html.parser")
