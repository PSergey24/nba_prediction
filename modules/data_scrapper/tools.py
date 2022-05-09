import requests
import pickle
from bs4 import BeautifulSoup


class PickleTools:

    @staticmethod
    def save_state(name, variable):
        with open(name, 'wb') as outp:
            pickle.dump(variable, outp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def get_state(name):
        with open(name, 'rb') as inp:
            state = pickle.load(inp)
        return state


class BSTools:

    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'lxml')

