import os
import pickle
import pandas as pd
from modules.data_handler.setting import NormalizerSetting
from modules.features_collector import FeatureCollector


class DataCollector:

    def __init__(self):
        self.teams = {}
        self.players_info = None
        self.players = {}
        self.players_last_10 = {}
        self.players_by_seasons = {}
        self.df = None

    def main(self):
        # self.save_players()
        self.get_teams()
        self.read_players()
        self.to_union_data()

    def get_teams(self):
        self.get_teams_data()
        self.get_teams_normalized_data()

    def get_teams_data(self):
        directory = NormalizerSetting.stats_directories['teams']
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        for file in files_list:
            df = pd.read_csv(directory + file)
            df = df.iloc[:, 3:12]
            df.drop(['record', 'inactive', 'ELO'], axis=1, inplace=True)
            df['previous_time'] = df.time.shift(1).fillna('')
            self.teams.update({file.split('_')[0]: df})
        print(f'teams are read')

    def get_teams_normalized_data(self):
        directory = NormalizerSetting.stats_directories['teams'] + 'normalized/'
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        for file in files_list:
            df = pd.read_csv(directory + file)
            self.teams[file.split('_')[0]] = pd.concat([self.teams[file.split('_')[0]], df['ELO']], axis=1)
        print(f'normalized teams are read')

    def read_players(self):
        self.players_info = self.get_info('data/clean_data/players.pkl')

    @staticmethod
    def get_info(name):
        with open(name, 'rb') as inp:
            stats = pickle.load(inp)
        return stats

    def to_union_data(self):
        list_games = []

        for team in self.teams:
            for i, team_1 in reversed(list(self.teams[team].iterrows())):
                feature_collector = FeatureCollector(team, team_1['opponent'], team_1['time'], False, self.players_info)
                features = feature_collector.main()

                winner = self.get_field_winner(features['home'], team_1)

                data = {'name_1': team, 'score': team_1['score'], 'name_2': team_1['opponent'], 'link': team_1['link']}
                data |= features
                data.update({'Y': winner})

                index = self.teams[team_1['opponent']].index[self.teams[team_1['opponent']]['time'] == team_1['time']].tolist()[0]

                list_games.append(data)
                self.teams[team].drop([i], axis=0, inplace=True)
                self.teams[team_1['opponent']].drop([index], axis=0, inplace=True)

            print(f'team was processed {team}')
        self.df = pd.DataFrame(list_games)
        self.df.to_csv('data/training_data/dataset_05_21_may.csv', encoding='utf-8')
        print('dataset was created')

    @staticmethod
    def get_field_winner(home, game):
        score = game['score'].split('-')
        if home == 1 and int(score[0]) > int(score[1]) or home == 0 and int(score[0]) < int(score[1]):
            winner = 0
        else:
            winner = 1
        return winner

    # save info about players to .pkl
    def save_players(self):
        directory = NormalizerSetting.stats_directories['players']
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        df_list = {}

        for file in files_list:
            df = pd.read_csv(directory + file)
            df_normalized = pd.read_csv(directory + 'normalized/' + file)
            df_10_games = pd.read_csv(NormalizerSetting.stats_directories['players_10_average'] + 'normalized/' + file)
            df_by_seasons = pd.read_csv(NormalizerSetting.stats_directories['players_season_average'] + file)
            df_by_seasons_normalized = pd.read_csv(NormalizerSetting.stats_directories['players_season_average'] + 'normalized/' + file)

            df = df.iloc[:, :7]
            df_by_seasons = df_by_seasons.iloc[:, 1:2]

            df_normalized.drop(['Unnamed: 0'], axis=1, inplace=True)
            df_10_games.drop(['Unnamed: 0'], axis=1, inplace=True)
            df_by_seasons_normalized.drop(['Unnamed: 0'], axis=1, inplace=True)

            name = file.replace('.csv', '')
            self.players.update({name: pd.concat([df, df_normalized], axis=1)})
            self.players_last_10.update({name: pd.concat([df, df_10_games], axis=1)})
            self.players_by_seasons.update({name: pd.concat([df_by_seasons, df_by_seasons_normalized], axis=1)})

            print(f'player was processed {name}')

        df_list.update({'players': self.players})
        df_list.update({'players_last_10': self.players_last_10})
        df_list.update({'players_by_seasons': self.players_by_seasons})
        self.save_info('data/clean_data/players.pkl', df_list)

    @staticmethod
    def save_info(name, variable):
        with open(name, 'wb') as outp:
            pickle.dump(variable, outp, pickle.HIGHEST_PROTOCOL)

