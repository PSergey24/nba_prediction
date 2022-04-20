from __future__ import annotations
import os.path
from typing import List
from .tools import PickleTools


class StateWorker:

    def __init__(self):
        self.file_way = 'data/row_data/state.pkl'
        self.pickle = PickleTools()

    def get_state(self) -> State:
        if os.path.exists(self.file_way) is True:
            return self.pickle.get_state(self.file_way)
        else:
            return State()

    def save_state(self, state: State) -> None:
        self.pickle.save_state(self.file_way, state)

    @staticmethod
    def get_seasons(start_season: int, last_season: int) -> List[str]:
        return ['https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_games.html'
                for year in range(start_season, last_season, 1)]

    @staticmethod
    def update_elo_rating(state: State) -> State:
        for key, value in state.teams_elo_rating.items():
            new_rating = (value * 0.75) + (1505 * 0.25)
            state.teams_elo_rating.update({key: new_rating})
        return state


class State:

    def __init__(self):
        self.seasons = []
        self.current_season_index = None
        self.games = []
        self.current_game_index = None
        self.teams_elo_rating = {}
