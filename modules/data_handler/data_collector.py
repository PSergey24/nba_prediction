import os
import pandas as pd
from modules.data_handler.setting import NormalizerSetting


class DataCollector:

    def __init__(self):
        self.teams = {}
        self.df = None

    def main(self):
        self.get_teams()
        self.get_players()
        self.to_union_data()

    def get_teams(self):
        self.get_teams_data()
        self.get_teams_normalized_data()
        print(1)

    def get_teams_data(self):
        directory = NormalizerSetting.stats_directories['teams']
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        for file in files_list:
            df = pd.read_csv(directory + file)
            df = df.iloc[:, 5:12]
            df.drop(['inactive', 'ELO'], axis=1, inplace=True)
            self.teams.update({file.split('_')[0]: df})
        print(f'teams are read')

    def get_teams_normalized_data(self):
        directory = NormalizerSetting.stats_directories['teams'] + 'normalized/'
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        for file in files_list:
            df = pd.read_csv(directory + file)
            self.teams[file.split('_')[0]] = pd.concat([self.teams[file.split('_')[0]], df['ELO']], axis=1)
        print(f'normalized teams are read')

    def get_players(self):
        pass

    def to_union_data(self):
        list_games = []

        for team in self.teams:
            for i, team_1 in reversed(list(self.teams[team].iterrows())):
                team_2 = self.teams[team_1['opponent']][self.teams[team_1['opponent']]['time'] == team_1['time']]

                home = self.get_field_home(team_1)
                winner = self.get_field_winner(home, team_1)

                data = {'team_1': team_1['ELO'], 'team_2': team_2['ELO'].values[0], 'home': home, 'Y': winner}

                index = team_2.axes[0].values[0]
                list_games.append(data)
                self.teams[team].drop([i], axis=0, inplace=True)
                self.teams[team_1['opponent']].drop([index], axis=0, inplace=True)

            print(f'team was processed {team}')
        self.df = pd.DataFrame(list_games)
        print(1)

    @staticmethod
    def get_field_home(game):
        return 1 if game['is_home'] is True else 0

    @staticmethod
    def get_field_winner(home, game):
        score = game['score'].split('-')
        if home == 1 and int(score[0]) > int(score[1]) or home == 0 and int(score[0]) < int(score[1]):
            winner = 0
        else:
            winner = 1
        return winner

