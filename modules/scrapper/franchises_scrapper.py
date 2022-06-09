import requests
from bs4 import BeautifulSoup
from modules.db_worker import DBWorker


class FranchisesScrapper:

    def __init__(self):
        self.link = 'https://www.basketball-reference.com/teams/'
        self.franchise_index = 0
        self.db_worker = DBWorker('data/db/nba.db')

    def get_all(self):
        rows = self.db_worker.get_all('franchises')
        [print(row) for row in rows]

    def main(self) -> None:
        soup = self.get_soup()
        franchises_list = self.parse_data(soup)
        self.insert_to_db(franchises_list)

    def get_soup(self):
        response = requests.get(self.link)
        return BeautifulSoup(response.text, "html.parser")

    def parse_data(self, soup):
        rows_active = self.parse_rows(soup, 'teams_active')
        rows_defunct = self.parse_rows(soup, 'teams_defunct')
        rows_active.extend(rows_defunct)
        return self.parse_franchises(rows_active)

    @staticmethod
    def parse_rows(soup, id_table):
        return soup.find('table', id=id_table).find_all(attrs={"class": ["full_table", "partial_table"]})

    def parse_franchises(self, rows):
        result = []
        for i, soup in enumerate(rows):
            self.check_index(soup)
            next_soup = soup.find_next_sibling("tr")
            if 'full_table' in soup.attrs['class'] and next_soup is not None and 'partial_table' in next_soup.attrs['class']:
                continue
            result.append(self.parse_franchise(soup))
        return result

    def check_index(self, soup):
        if soup.find('th').find('a') is not None:
            self.franchise_index += 1

    def parse_franchise(self, soup):
        name = self.get_team_name(soup)
        lg = self.get_lg_id(soup)
        first_year = self.get_first_year(soup)
        last_year = self.get_last_year(soup)
        return {'id_franchise': self.franchise_index, 'name': name, 'lg': lg, 'first_season': first_year, 'last_season': last_year}

    @staticmethod
    def get_team_name(soup):
        return soup.find('th').text

    @staticmethod
    def get_lg_id(soup):
        return soup.find(attrs={"data-stat": 'lg_id'}).text

    @staticmethod
    def get_first_year(soup):
        cell = soup.find(attrs={"data-stat": 'year_min'}).text
        year = int(cell.split('-')[0]) + 1
        return year

    @staticmethod
    def get_last_year(soup):
        cell = soup.find(attrs={"data-stat": 'year_max'}).text
        year = int(cell.split('-')[0]) + 1
        return year

    def insert_to_db(self, franchises_list):
        [self.insert_item_to_db(item) for item in franchises_list]

    def insert_item_to_db(self, item):
        columns = ', '.join(item.keys())
        values = [int(x) if isinstance(x, bool) else x for x in item.values()]
        self.db_worker.insert('franchises', columns, values)

