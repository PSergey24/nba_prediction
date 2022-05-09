import os
import pandas as pd


class DataCleaner:

    def main(self):
        self.update_data()

    def update_data(self):
        self.update_players_data()
        self.update_teams_data()

    def update_players_data(self):
        directory = 'data/raw_data/players/'
        players_list = [name for name in os.listdir(directory) if '.csv' in name]

        for player in players_list:
            way_raw_data = directory + player
            df = pd.read_csv(way_raw_data)
            self.update_player_data(df, player)
            print(f'processed player: {player}')

    def update_player_data(self, df, name):
        self.update_average_player_data(df, name)
        self.update_last_game_player_data(df.copy(), name)

    @staticmethod
    def update_average_player_data(df, name):
        way = 'data/clean_data/players/seasons_average/' + name

        season_average = df.groupby('season').mean().round(3).reset_index().drop(['is_home'], axis=1)
        season_average.to_csv(way, encoding='utf-8')

    @staticmethod
    def update_last_game_player_data(df, name):
        way = 'data/clean_data/players/10_games_average/' + name

        time_field = df.pop('time')
        df.drop(['is_home', 'minutes', 'opponent', 'score', 'team'], axis=1, inplace=True)
        rolling_windows = df.groupby('season').rolling(10, min_periods=1)
        last_games = rolling_windows.mean().round(3).reset_index().drop(['level_1'], axis=1)
        last_games.insert(1, 'time', time_field)
        last_games.to_csv(way, encoding='utf-8')

    def update_teams_data(self):
        directory = 'data/raw_data/teams/'
        teams_list = [name for name in os.listdir(directory) if '.csv' in name]

        for team in teams_list:
            way_raw_data = directory + team
            df = pd.read_csv(way_raw_data)
            self.update_team_data(df, team)
            print(f'processed team: {team}')

    def update_team_data(self, df, team):
        self.update_last_game_team_data(df.copy(), team)
        self.clear_team_data(df.copy(), team)

    @staticmethod
    def update_last_game_team_data(df, name):
        way = 'data/clean_data/teams/10_games_average/' + name

        df = df.iloc[:, :28]
        time_field = df.pop('time')
        df.drop(['season_stage', 'link', 'record', 'is_home', 'opponent', 'score', 'roster', 'inactive'], axis=1, inplace=True)
        rolling_windows = df.groupby('season').rolling(10, min_periods=1)
        last_games = rolling_windows.mean().round(3).reset_index().drop(['level_1'], axis=1)
        last_games.insert(1, 'time', time_field)
        last_games.to_csv(way, encoding='utf-8')

    @staticmethod
    def clear_team_data(df, name):
        way = 'data/clean_data/teams/cleaned/' + name
        df = df.iloc[:, :28]
        df.to_csv(way, encoding='utf-8')
