import pandas as pd


class FeatureCollector:

    def __init__(self, team_1, team_2, date, new_game, players_info=None):
        self.new_game = new_game
        self.names = [team_1, team_2]
        self.date = date
        self.players_info = players_info

    def main(self):
        team_1 = self.get_teams_info(1)
        team_2 = self.get_teams_info(2)

        t1_is_b2b = self.get_field_b2b_game(self.date, team_1['previous_game_time'])
        t2_is_b2b = self.get_field_b2b_game(self.date, team_2['previous_game_time'])

        players_1 = self.get_players(team_1['roster'], 1)
        players_2 = self.get_players(team_2['roster'], 2)

        data = {'team_1': team_1['ELO'], 'team_2': team_2['ELO']}

        data |= players_1
        data |= players_2

        data.update({'t1_b2b': t1_is_b2b, 't2_b2b': t2_is_b2b, 'home': team_1['is_home']})
        return data

    def get_teams_info(self, team_index):
        team = self.names[team_index - 1]

        games_normalized = pd.read_csv('data/clean_data/teams/cleaned/normalized/' + team + '_games.csv', index_col=0)
        games = pd.read_csv('data/clean_data/teams/cleaned/' + team + '_games.csv', index_col=0)

        index = self.get_index_game(games)

        elo = self.get_elo(index, games_normalized)
        previous_time = self.get_previous_game_time(index, games)
        roster = self.get_roster(index, team, games)
        is_home = self.is_home(index, games, team_index)
        team_info = {'ELO': elo, 'previous_game_time': previous_time, 'is_home': is_home, 'roster': roster}
        return team_info

    def get_index_game(self, games):
        list_indexes = games.index[games['time'] == self.date].tolist()
        return list_indexes[0] if len(list_indexes) > 0 else None

    @staticmethod
    def get_elo(index, df):
        return df['ELO'].iloc[-1] if index is None else df['ELO'].iloc[index]

    @staticmethod
    def get_previous_game_time(index, df):
        return df['time'].iloc[-1] if index is None else df['time'].iloc[index - 1]

    @staticmethod
    def get_roster(index, team, games):
        if index is None:
            roster = pd.read_csv('data/roster/' + team + '.csv')
            roster = [item['players'] for index, item in roster.iterrows()]
        else:
            roster = games['roster'].iloc[index]
            roster = [item.strip() for item in roster.split(',')]
        return roster

    @staticmethod
    def is_home(index, df, i):
        if index is None and i == 1:
            return 0
        elif index is None and i == 2:
            return 1
        else:
            return int(df['is_home'].iloc[index])

    @staticmethod
    def get_field_b2b_game(current_time, previous_time):
        if previous_time == '' or current_time == '':
            return 0

        current = int(current_time.split(',')[-2].split()[-1])
        previous = int(previous_time.split(',')[-2].split()[-1])
        return 1 if current - previous == 1 else 0

    def get_players(self, input_list, team_index):
        player_list = []
        for player in input_list:
            per, seconds = self.get_player_info(player)
            player_dict = {'name': player, 'PER': per, 'seconds': seconds}
            player_list.append(player_dict)
        return self.to_filter_players(player_list, team_index)

    @staticmethod
    def get_players_list(team):
        return pd.read_csv('data/roster/' + team + '.csv')

    def get_player_info(self, player_name):
        player = self.get_player_info_normal(player_name)
        player_normalized = self.get_player_info_normalized(player_name)
        list_indexes = player.index[player['time'] == self.date].tolist()
        per = player_normalized['PER'].iloc[list_indexes[0]] if len(list_indexes) > 0 else player_normalized['PER'].iloc[-1]
        seconds = player['seconds'].iloc[list_indexes[0]] if len(list_indexes) > 0 else player['seconds'].iloc[-1]
        return per, seconds

    def get_player_info_normal(self, name):
        return pd.read_csv('data/clean_data/players/10_games_average/' + name + '.csv') if self.new_game is True else self.players_info['players'][name]

    def get_player_info_normalized(self, name):
        return pd.read_csv('data/clean_data/players/10_games_average/normalized/' + name + '.csv') if self.new_game is True else self.players_info['players_last_10'][name]

    @staticmethod
    def to_filter_players(player_list, team_index):
        player_list = sorted(player_list, key=lambda d: d['PER'], reverse=True)
        player_list = player_list[:8]

        d = {}
        for i, player in enumerate(player_list):
            d.update({'t' + str(team_index) + '_p' + str(i) + '_per': player['PER']})
        return d
