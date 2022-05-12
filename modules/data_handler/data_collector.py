import os
import pickle
import pandas as pd
from modules.data_handler.setting import NormalizerSetting


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
                team_2 = self.teams[team_1['opponent']][self.teams[team_1['opponent']]['time'] == team_1['time']]

                home = self.get_field_home(team_1)
                winner = self.get_field_winner(home, team_1)
                t1_is_b2b = self.get_field_b2b_game(team_1['time'], team_1['previous_time'])
                t2_is_b2b = self.get_field_b2b_game(team_2['time'].values[0], team_2['previous_time'].values[0])
                players_1 = self.get_field_players(team_1['roster'], team_1['time'], 1)
                players_2 = self.get_field_players(team_2['roster'].values[0], team_1['time'], 2)

                data = {'name_1': team, 'score': team_1['score'], 'name_2': team_1['opponent'], 'link': team_1['link'],
                        'team_1': team_1['ELO'], 'team_2': team_2['ELO'].values[0]}
                data |= players_1
                data |= players_2
                data.update({'t1_b2b': t1_is_b2b, 't2_b2b': t2_is_b2b, 'home': home, 'Y': winner})

                index = team_2.axes[0].values[0]
                list_games.append(data)
                self.teams[team].drop([i], axis=0, inplace=True)
                self.teams[team_1['opponent']].drop([index], axis=0, inplace=True)

            print(f'team was processed {team}')
        self.df = pd.DataFrame(list_games)
        self.df.to_csv('data/training_data/dataset_03.csv', encoding='utf-8')
        print('dataset was created')

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

    @staticmethod
    def get_field_b2b_game(current_time, previous_time):
        if previous_time == '' or current_time == '':
            return 0

        current = int(current_time.split(',')[-2].split()[-1])
        previous = int(previous_time.split(',')[-2].split()[-1])
        return 1 if current - previous == 1 else 0

    def get_field_players(self, players, time, team):
        players_per = []
        players_list = players.split(',')

        for player in players_list:
            field = self.players_info['players_last_10'][player.strip()][self.players_info['players_last_10'][player.strip()]['time'] == time]
            players_per.append(field['PER'].values[0])

        players_per.sort(reverse=True)
        if len(players_per) < 8:
            while len(players_per) < 8:
                players_per.append(-1)

        players_per = players_per[:8]
        d = {'t' + str(team) + '_p' + str(i) + '_per': players_per[i] for i in range(0, len(players_per), 1)}
        return d

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

