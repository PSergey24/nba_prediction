import os
import pickle
import pandas as pd
from modules.data_handler.setting import NormalizerSetting


class DataNormalizer:

    def __init__(self, players_list=None, teams_list=None):
        self.players_list = players_list
        self.teams_list = teams_list

        self.min_max_stats = {'teams': None, 'teams_10_average': None, 'players': None, 'players_10_average': None,
                              'players_season_average': None}

    def save_min_max_stats(self):
        for key, directory in NormalizerSetting.stats_directories.items():
            df = self.get_data(directory, NormalizerSetting.stats_drop_lists[key])
            self.min_max_stats[key] = df.apply(self.get_min_max)
        self.save_stats('data/clean_data/min_max_stats.pkl', self.min_max_stats)

    @staticmethod
    def get_data(directory, drop_list):
        files_list = [name for name in os.listdir(directory) if '.csv' in name]
        df_list = (pd.read_csv(directory + file, engine='python',
                               on_bad_lines='skip', encoding='utf8') for file in files_list)
        big_df = pd.concat(df_list, ignore_index=True)
        big_df.drop(drop_list, axis=1, inplace=True)
        return big_df

    @staticmethod
    def get_min_max(x):
        return pd.Series(index=['min', 'max'], data=[x.min(), x.max()])

    @staticmethod
    def save_stats(name, variable):
        with open(name, 'wb') as outp:
            pickle.dump(variable, outp, pickle.HIGHEST_PROTOCOL)

    def to_normalize_data(self):
        self.min_max_stats = self.get_stats('data/clean_data/min_max_stats.pkl')
        self.correct_min_max()
        self.to_normalize_category('teams')
        self.to_normalize_category('players')

    @staticmethod
    def get_stats(name):
        with open(name, 'rb') as inp:
            stats = pickle.load(inp)
        return stats

    def correct_min_max(self):
        extreme_values = {'PER': {'max': 45, 'min': -45}}
        for key, item in self.min_max_stats.items():
            for k in extreme_values:
                if k in list(item):
                    item.loc['max', k] = extreme_values[k]['max']
                    item.loc['min', k] = extreme_values[k]['min']

    def to_normalize_category(self, category):
        for key, directory in NormalizerSetting.stats_directories.items():
            if category not in directory:
                continue

            files_list = self.get_files_list(directory, category)
            for file in files_list:
                df = pd.read_csv(directory + file)
                df.drop(NormalizerSetting.stats_drop_lists[key], axis=1, inplace=True)
                column_names = df.columns.values.tolist()
                for column in column_names:
                    df[column] = self.to_normalize(df[column], self.min_max_stats[key][column])

                way = directory + 'normalized/' + file
                df.to_csv(way, encoding='utf-8')
                print(f'normalized file: {file}')

    def get_files_list(self, directory, category):
        if category == 'players' and self.players_list is None or category == 'teams' and self.teams_list is None:
            return [name for name in os.listdir(directory) if '.csv' in name]
        elif category == 'players' and self.players_list is not None:
            return self.players_list
        elif category == 'teams' and self.teams_list is not None:
            return self.teams_list

    @staticmethod
    def to_normalize(column, y):
        for i, value in enumerate(column):
            if value < y['min']:
                column[i] = y['min']
            if value > y['max']:
                column[i] = y['max']

        return [round(2 * ((x - y['min']) / (y['max'] - y['min'])) - 1, 3) for x in column]
