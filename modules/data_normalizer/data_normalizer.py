import os
import pickle
import pandas as pd
from modules.data_normalizer.setting import NormalizerSetting


class DataNormalizer:

    def __init__(self):
        self.min_max_stats = {'teams': None, 'teams_10_average': None, 'players': None, 'players_10_average': None,
                              'players_season_average': None}

    def get_stats(self):
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
