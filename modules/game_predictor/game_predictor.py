import torch
import pandas as pd
from modules.models.logistic_regression import LogisticRegression


class GamePredictor:

    def __init__(self):
        self.model = LogisticRegression(21, 264, 1)

        self.get_weights()

    def get_weights(self):
        self.model.load_state_dict(torch.load('model/model.pth'))
        self.model.eval()

    def main(self):
        df = self.get_schedule()
        self.process_games(df)

    @staticmethod
    def get_schedule():
        return pd.read_csv('data/schedule/schedule.csv')

    def process_games(self, df):
        for index, game in df.iterrows():
            features = self.process_game(game)
            self.to_predict(features)
            print(1)

    def process_game(self, game):
        team_1 = self.get_teams_info(game['visitor'])
        team_2 = self.get_teams_info(game['home'])

        t1_is_b2b = self.get_field_b2b_game(game['date'], team_1['time'])
        t2_is_b2b = self.get_field_b2b_game(game['date'], team_2['time'])

        players_1 = self.get_players(game['visitor'], 1)
        players_2 = self.get_players(game['home'], 2)

        data = {'name_1': game['visitor'], 'name_2': game['home'],
                'team_1': team_1['ELO'], 'team_2': team_2['ELO']}

        data |= players_1
        data |= players_2

        data.update({'t1_b2b': t1_is_b2b, 't2_b2b': t2_is_b2b, 'home': 0})
        return data

    @staticmethod
    def get_teams_info(team):
        games_normalized = pd.read_csv('data/clean_data/teams/cleaned/normalized/' + team + '_games.csv')
        games = pd.read_csv('data/clean_data/teams/cleaned/' + team + '_games.csv')
        team_info = {'ELO': games_normalized['ELO'].iloc[-1], 'time': games['time'].iloc[-1]}
        return team_info

    @staticmethod
    def get_field_b2b_game(current_time, previous_time):
        if previous_time == '' or current_time == '':
            return 0

        current = int(current_time.split(',')[-2].split()[-1])
        previous = int(previous_time.split(',')[-2].split()[-1])
        return 1 if current - previous == 1 else 0

    def get_players(self, team, team_index):
        player_list = []
        df_players_list = self.get_players_list(team)
        for index, player in df_players_list.iterrows():
            per = self.get_player(player['players'])
            player_dict = {'name': player, 'PER': per}
            player_list.append(player_dict)
        return self.to_filter_players(player_list, team_index)

    @staticmethod
    def to_filter_players(player_list, team_index):
        player_list = sorted(player_list, key=lambda d: d['PER'], reverse=True)
        # if team_index == 2:
        #     player_list = sorted(player_list, key=lambda d: d['PER'])
        player_list = player_list[:8]

        d = {}
        for i, player in enumerate(player_list):
            d.update({'t' + str(team_index) + '_p' + str(i) + '_per': player['PER']})
        return d

    @staticmethod
    def get_players_list(team):
        player = pd.read_csv('data/roster/' + team + '.csv')
        return player

    @staticmethod
    def get_player(player):
        player = pd.read_csv('data/clean_data/players/10_games_average/normalized/' + player + '.csv')
        return player['PER'].iloc[-1]

    def to_predict(self, features):
        visitor = features.pop('name_1')
        home = features.pop('name_2')

        data = torch.FloatTensor([recs for recs in features.values()])
        prediction = self.model(data)
        print(f'{visitor} wins {home} with a {round(prediction.item(), 3)} percent chance')