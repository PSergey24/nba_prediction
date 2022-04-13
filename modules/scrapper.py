import pickle
import os.path
from .setting import ScrapperSetting
from .season_scrapper import SeasonScrapper


class DataScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()
        self.season_scrapper = None
        self.seasons = []
        self.state_name = 'data/row_data/state.pkl'
        self.state = None

    def main(self):
        # self.test()
        self.get_state()
        self.get_seasons()
        self.process_seasons()
        print(f'Finished')

    def get_state(self):
        is_exist = os.path.exists(self.state_name)
        if is_exist is True:
            with open(self.state_name, 'rb') as inp:
                self.state = pickle.load(inp)
        else:
            self.state = ParsingState()

    def get_seasons(self):
        if len(self.state.seasons) == 0:
            self.seasons = ['https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_games.html' for year in range(2020, 2023, 1)]
            self.state.seasons = self.seasons
            self.state.current_season = 0
        else:
            self.seasons = self.state.seasons

    def process_seasons(self):
        for i in range(self.state.current_season, len(self.state.seasons), 1):
            url = self.seasons[i]
            self.season_scrapper = SeasonScrapper(url, self.state, self.state_name)
            self.season_scrapper.main()

            # update state
            self.state.current_season += 1
            self.state.games.clear()
            self.state.current_game = None
            self.save_state()

    def save_state(self):
        with open(self.state_name, 'ab') as outp:
            pickle.dump(self.state, outp, pickle.HIGHEST_PROTOCOL)

    def test(self):
        url = 'https://www.basketball-reference.com/leagues/NBA_2020_games.html'
        self.season_scrapper = SeasonScrapper(url, self.state, self.state_name)
        self.season_scrapper.test()


class ParsingState:

    def __init__(self):
        self.seasons = []
        self.current_season = None
        self.games = []
        self.current_game = None
