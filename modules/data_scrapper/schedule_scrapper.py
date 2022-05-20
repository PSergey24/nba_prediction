import pandas as pd
from .tools import BSTools
from .season_scrapper import SeasonScrapper


class ScheduleScrapper:

    def __init__(self):
        self.bs_tools = BSTools()
        self.season_scrapper = SeasonScrapper('https://www.basketball-reference.com/leagues/NBA_2022_games.html')

    def main(self):
        self.season_scrapper.get_soup()
        self.season_scrapper.parse_list_months()
        games_list = self.season_scrapper.get_list_games()
        self.update_schedule(games_list)

    @staticmethod
    def update_schedule(games_list):
        games_list = [item for item in games_list if item['link'] is None]
        df = pd.DataFrame(games_list, columns=['date', 'visitor', 'home'])
        df.to_csv('data/schedule/schedule.csv', index=False)
