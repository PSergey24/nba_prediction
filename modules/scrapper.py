from .setting import ScrapperSetting
from .game_scrapper import GameScrapper


class DataScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()
        self.game_scrapper = None

    def main(self):
        url = 'https://www.basketball-reference.com/boxscores/202008140HOU.html'

        self.game_scrapper = GameScrapper(url)
        self.game_scrapper.main()
        print(1)
