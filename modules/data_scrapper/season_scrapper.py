import time
from typing import List
from bs4 import BeautifulSoup
from .setting import ScrapperSetting
from .tools import BSTools
from .game_scrapper import GameScrapper
from .state_worker import StateWorker, State


class SeasonScrapper:

    def __init__(self, link: str, state: State = None):
        self.setting = ScrapperSetting()
        self.state_worker = StateWorker()
        self.bs_tools = BSTools()
        self.game_scrapper = None

        self.link = link
        self.state = state

        self.soup = None
        self.season = None
        self.months = []
        self.games = []

    def main(self) -> None:
        self.get_soup()
        self.parse_data()
        self.process_games()
        print(f'Season was parsed and processed: {self.season}')

    def get_soup(self):
        self.soup = self.bs_tools.get_soup(self.link)

    def parse_data(self) -> None:
        self.parse_season_name()
        self.parse_list_months()
        self.parse_list_games()

    def parse_season_name(self) -> None:
        self.season = self.soup.find('h1').find('span').text

    def parse_list_months(self) -> None:
        month_block = self.soup.find('div', class_='filter')
        month_list = month_block.find_all('a')
        self.months = ['https://www.basketball-reference.com' + month['href'] for month in month_list]

    def parse_list_games(self) -> None:
        games_list = self.get_list_games()
        games_list = [item['link'] for item in games_list if item['link'] is not None]
        if len(games_list) > len(self.state.games):
            if not self.state.games:
                self.state.current_game_index = 0
            self.state.games = games_list
            print(f'Links of games was parsed: season {self.season}, count {len(games_list)}')
        self.games = self.state.games

    def get_list_games(self) -> List[dict]:
        return [item for month in self.months for item in self.process_month(month)]

    def process_month(self, month: str) -> List[dict]:
        soup_month = self.bs_tools.get_soup(month)
        rows = soup_month.find('tbody').find_all("tr", {'class': None})
        games_list = []
        for row in rows:
            a = row.find("td", {"data-stat": "box_score_text"}).find('a')
            link = None if a is None else 'https://www.basketball-reference.com' + a['href']
            date = row.find(attrs={"data-stat": "date_game"}).text
            visitor = row.find(attrs={"data-stat": "visitor_team_name"}).find('a')['href'].split('/')[-2]
            home = row.find(attrs={"data-stat": "home_team_name"}).find('a')['href'].split('/')[-2]
            game = {'date': date, 'visitor': visitor, 'home': home, 'link': link}
            games_list.append(game)
        return games_list

    def process_games(self) -> None:
        for i in range(self.state.current_game_index, len(self.state.games), 1):
            self.process_game(i)
            self.update_state()
            time.sleep(2)

    def process_game(self, index: int) -> None:
        self.game_scrapper = GameScrapper(self.games[index], self.season, self.state)
        self.game_scrapper.main()

    def update_state(self) -> None:
        self.state.current_game_index += 1
        self.save_state()

    def save_state(self) -> None:
        self.state_worker.save_state(self.state)

    def test(self) -> None:
        url = 'https://www.basketball-reference.com/boxscores/202204180GSW.html'
        self.game_scrapper = GameScrapper(url, '2000', State())
        self.game_scrapper.main()
        print(1)
