import requests
import pickle
from bs4 import BeautifulSoup


class Tools:
    # get list of stats/columns
    @staticmethod
    def get_table_fields():
        url = 'https://www.basketball-reference.com/boxscores/202008140HOU.html'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        table_list = ['box-PHI-game-basic', 'box-PHI-game-advanced']
        stats = {}
        for item in table_list:
            table = soup.find(id=item)
            starters = table.find(text="Starters")
            starters_parent = starters.parent.parent
            th_list = starters_parent.find_all('th')

            for th in th_list:
                data_stat = th['data-stat']
                text = th.text
                stats.update({data_stat.lower(): text.lower()})
        print(stats)


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

