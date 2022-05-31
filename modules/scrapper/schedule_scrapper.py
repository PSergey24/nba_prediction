from .tools import BSTools
from modules.db_worker import DBWorker


class ScheduleScrapper:

    def __init__(self):
        self.bs_tools = BSTools()
        self.link = 'https://www.basketball-reference.com/leagues/NBA_2022_games.html'
        self.soup = self.bs_tools.get_soup(self.link)
        self.db_worker = DBWorker('data/db/nba.db')
        self.months = None
        self.games = None

    def main(self):
        self.parse_list_months()
        self.get_list_games()
        self.update_schedule()
        self.db_worker.conn.close()

    def parse_list_months(self) -> None:
        month_block = self.soup.find('div', class_='filter')
        month_list = month_block.find_all('a')
        self.months = ['https://www.basketball-reference.com' + month['href'] for month in month_list]

    def get_list_games(self):
        self.games = [item for month in self.months for item in self.process_month(month)]

    def process_month(self, month: str) -> list:
        soup_month = self.bs_tools.get_soup(month)
        rows = soup_month.find('tbody').find_all("tr", {'class': None})
        return [self.process_table_row(row) for row in rows]

    @staticmethod
    def process_table_row(row):
        a = row.find("td", {"data-stat": "box_score_text"}).find('a')
        link = None if a is None else 'https://www.basketball-reference.com' + a['href']
        date = row.find(attrs={"data-stat": "date_game"}).text
        time = row.find(attrs={"data-stat": "game_start_time"}).text
        visitor_name = row.find(attrs={"data-stat": "visitor_team_name"}).find('a').text
        home_name = row.find(attrs={"data-stat": "home_team_name"}).find('a').text
        if time == '':
            return {'link': link, 'date': f'{date}', 'visitor': visitor_name, 'home': home_name}
        return {'link': link, 'date': f'{time}, {date}', 'visitor': visitor_name, 'home': home_name}

    def update_schedule(self):
        next_games = [{'date': item['date'], 'visitor': item['visitor'], 'home': item['home']} for item in self.games if item['link'] is None]
        self.insert_to_db(next_games)

    def insert_to_db(self, franchises_list):
        self.db_worker.clear_table('SCHEDULE')
        self.db_worker.reset_ai('SCHEDULE')
        [self.insert_item_to_db(item) for item in reversed(franchises_list)]

    def insert_item_to_db(self, item):
        columns = ', '.join(item.keys())
        values = [int(x) if isinstance(x, bool) else x for x in item.values()]
        self.db_worker.insert('SCHEDULE', columns, values)
