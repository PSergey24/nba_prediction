import time
from typing import List
from bs4 import BeautifulSoup
from .setting import ScrapperSetting
from .tools import BSTools
from .game_scrapper import GameScrapper
from .state_worker import StateWorker, State


class SeasonScrapper:

    def __init__(self, link: str, state: State):
        self.setting = ScrapperSetting()
        self.state_worker = StateWorker()
        self.bs_tools = BSTools()
        self.game_scrapper = None

        self.link = link
        self.state = state

        self.season = None
        self.months = []
        self.games = []

    def main(self) -> None:
        soup = self.bs_tools.get_soup(self.link)
        self.parse_data(soup)
        self.process_games()
        print(f'Season was parsed and processed: {self.season}')

    def parse_data(self, soup: BeautifulSoup) -> None:
        self.parse_season_name(soup)
        self.parse_list_months(soup)
        self.parse_list_games()

    def parse_season_name(self, soup: BeautifulSoup) -> None:
        self.season = soup.find('h1').find('span').text

    def parse_list_months(self, soup: BeautifulSoup) -> None:
        month_block = soup.find('div', class_='filter')
        month_list = month_block.find_all('a')
        self.months = ['https://www.basketball-reference.com' + month['href'] for month in month_list]

    def parse_list_games(self) -> None:
        games_list = self.get_list_games()
        if len(games_list) > len(self.state.games):
            if not self.state.games:
                self.state.current_game_index = 0
            self.state.games = games_list
            print(f'Links of games was parsed: season {self.season}, count {len(games_list)}')
        self.games = self.state.games

    def get_list_games(self) -> List[str]:
        game_list = []
        for month in self.months:
            game_list.extend(self.process_month(month))
        return game_list

    def process_month(self, month: str) -> List[str]:
        soup_month = self.bs_tools.get_soup(month)
        games = soup_month.find_all("td", {"data-stat": "box_score_text"})
        games_list = ['https://www.basketball-reference.com' + game.find('a')['href'] for game in games
                      if game.find('a') is not None]
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
