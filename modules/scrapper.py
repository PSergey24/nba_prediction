from .setting import ScrapperSetting
from .season_scrapper import SeasonScrapper
from .state_worker import StateWorker


class DataScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()
        self.state_worker = StateWorker()
        self.season_scrapper = None
        self.state = None
        self.seasons = []

    def main(self):
        self.get_state()
        self.get_seasons()
        self.process_seasons()
        print(f'Finished')

        # self.test()

    def get_state(self) -> None:
        self.state = self.state_worker.get_state()

    def get_seasons(self) -> None:
        if not self.state.seasons:
            self.state.seasons = self.state_worker.get_seasons(2000, 2023)
            self.state.current_season_index = 0
        self.seasons = self.state.seasons

    def process_seasons(self) -> None:
        for i in range(self.state.current_season_index, len(self.state.seasons), 1):
            self.process_season(i)
            # self.update_state()

    def process_season(self, index: int) -> None:
        self.season_scrapper = SeasonScrapper(self.seasons[index], self.state)
        self.season_scrapper.main()

    def update_state(self):
        self.update_elo_after_season()
        self.state.current_season_index += 1
        self.state.games.clear()
        self.state.current_game_index = None
        self.save_state()

    def update_elo_after_season(self) -> None:
        self.state = self.state_worker.update_elo_rating(self.state)

    def save_state(self) -> None:
        self.state_worker.save_state(self.state)

    def test(self) -> None:
        url = 'https://www.basketball-reference.com/leagues/NBA_2000_games.html'
        self.season_scrapper = SeasonScrapper(url, self.state)
        self.season_scrapper.test()
