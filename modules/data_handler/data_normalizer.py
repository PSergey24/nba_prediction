import os
import pickle
import pandas as pd
from modules.data_handler.setting import NormalizerSetting


class DataNormalizer:

    def __init__(self):
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

        for key, directory in NormalizerSetting.stats_directories.items():
            files_list = [name for name in os.listdir(directory) if '.csv' in name]
            for file in files_list:
                df = pd.read_csv(directory + file)
                df.drop(NormalizerSetting.stats_drop_lists[key], axis=1, inplace=True)
                column_names = df.columns.values.tolist()
                for column in column_names:

                    self.min_max_stats[key][column] = self.correct_min_max(column, self.min_max_stats[key][column])
                    df[column] = self.to_normalize(df[column], self.min_max_stats[key][column])

                way = directory + 'normalized/' + file
                df.to_csv(way, encoding='utf-8')
                print(f'processed file: {file}')
            print(f'processed directory: {directory}')

    @staticmethod
    def get_stats(name):
        with open(name, 'rb') as inp:
            stats = pickle.load(inp)
        return stats

    @staticmethod
    def correct_min_max(column, ds):
        extreme_values = {'PER': {'max': 45, 'min': -45}}
        if column in extreme_values:
            ds['max'] = extreme_values[column]['max']
            ds['min'] = extreme_values[column]['min']
        return ds

    @staticmethod
    def to_normalize(column, y):
        for i, value in enumerate(column):
            if value < y['min']:
                column[i] = y['min']
            if value > y['max']:
                column[i] = y['max']

        return [round(2 * ((x - y['min']) / (y['max'] - y['min'])) - 1, 3) for x in column]
