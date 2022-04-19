import os.path
from .setting import ScrapperSetting
from .tools import PickleTools
from .season_scrapper import SeasonScrapper


class DataScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()
        self.pickle = PickleTools()
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
            self.state = self.pickle.get_state(self.state_name)
        else:
            self.state = ParsingState()

    def get_seasons(self):
        if len(self.state.seasons) == 0:
            self.seasons = ['https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_games.html' for year in
                            range(2000, 2023, 1)]
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
            self.update_elo_after_season()
            self.state.current_season += 1
            self.state.games.clear()
            self.state.current_game = None
            self.pickle.save_state(self.state_name, self.state)

    def update_elo_after_season(self):
        elo_state = self.pickle.get_state('data/row_data/elo.pkl')
        for key, value in elo_state.teams.items():
            new_rating = (value * 0.75) + (1505 * 0.25)
            elo_state.teams.update({key: new_rating})
        self.pickle.save_state('data/row_data/elo.pkl', elo_state)

    def test(self):
        url = 'https://www.basketball-reference.com/leagues/NBA_2000_games.html'
        self.season_scrapper = SeasonScrapper(url, self.state, self.state_name)
        self.season_scrapper.test()


class ParsingState:

    def __init__(self):
        self.seasons = []
        self.current_season = None
        self.games = []
        self.current_game = None
