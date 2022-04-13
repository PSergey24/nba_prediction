import time
import pickle
import requests
from bs4 import BeautifulSoup
from .setting import ScrapperSetting
from .game_scrapper import GameScrapper


class SeasonScrapper:

    def __init__(self, link, state, state_name):
        self.link = link
        self.state = state
        self.state_name = state_name

        self.setting = ScrapperSetting()
        self.game_scrapper = None

        self.season = None
        self.month = []
        self.games = []

    def test(self):
        url = 'https://www.basketball-reference.com/boxscores/202008140HOU.html'
        url = 'https://www.basketball-reference.com/boxscores/201910220TOR.html'
        url = 'https://www.basketball-reference.com/boxscores/201405080MIA.html'

        self.game_scrapper = GameScrapper(url, '2000')
        self.game_scrapper.main()
        print(1)

    def main(self):
        soup = self.get_soup(self.link)
        self.parse_data(soup)
        print(f'Season was parsed and processed: {self.season}')

    @staticmethod
    def get_soup(url):
        response = requests.get(url)
        return BeautifulSoup(response.text, 'lxml')

    def parse_data(self, soup):
        self.parse_season(soup)
        self.parse_months(soup)
        self.parse_games()
        self.process_games()

    def parse_season(self, soup):
        h1 = soup.find('h1')
        self.season = h1.find('span').text

    def parse_months(self, soup):
        month_block = soup.find('div', class_='filter')
        month_list = month_block.find_all('a')
        for month in month_list:
            self.month.append('https://www.basketball-reference.com' + month['href'])

    def parse_games(self):
        if len(self.state.games) == 0:
            for month in self.month:
                soup_month = self.get_soup(month)
                games = soup_month.find_all("td", {"data-stat": "box_score_text"})
                for game in games:
                    game_link = game.find('a')
                    self.games.append('https://www.basketball-reference.com' + game_link['href'])

            self.state.games = self.games
            self.state.current_game = 0
            print(f'Links of games was parsed: season {self.season}, count {len(self.games)}')
        else:
            self.games = self.state.games

    def process_games(self):
        for i in range(self.state.current_game, len(self.state.games), 1):
            game = self.games[i]
            self.game_scrapper = GameScrapper(game, self.season)
            self.game_scrapper.main()

            # update state
            self.state.current_game += 1
            self.save_state()
            print(f'State was updated')
            time.sleep(4)

    def save_state(self):
        with open(self.state_name, 'wb') as outp:
            pickle.dump(self.state, outp, pickle.HIGHEST_PROTOCOL)