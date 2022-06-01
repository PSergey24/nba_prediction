import pandas as pd
from tqdm import tqdm
from datetime import date
from modules.db_worker import DBWorker


class FeatureCollectorDB:

    def __init__(self):
        self.db_worker = DBWorker('data/db/nba.db')

    def prediction(self, visitor, home, current_date):
        features = {}
        visitor_last_game = self.db_worker.get_last_game(visitor)
        home_last_game = self.db_worker.get_last_game(home)

        id_visitor = visitor_last_game['id_franchise']
        id_home = home_last_game['id_franchise']

        players_visitor = self.db_worker.get_active_players(id_visitor)
        players_home = self.db_worker.get_active_players(id_home)

        is_b2b_visitor = self.is_b2b(current_date, visitor_last_game['date'])
        is_b2b_home = self.is_b2b(current_date, home_last_game['date'])

        list_per_visitor = self.process_players(players_visitor, 1)
        list_per_home = self.process_players(players_home, 2)

        features.update({'ELO_visitor': visitor_last_game['ELO']})
        features.update({'ELO_home': home_last_game['ELO']})
        features |= list_per_visitor
        features |= list_per_home
        features.update({'visitor_b2b': is_b2b_visitor})
        features.update({'home_b2b': is_b2b_home})
        return features

    def main(self):
        games = self.get_games()
        df_games = self.to_df(games)
        normalized = self.to_normalize_data(df_games)
        self.save_data(normalized)
        self.db_worker.conn.close()

    def get_games(self):
        games = self.db_worker.get_all_games()

        for game in tqdm(games, desc='Games collecting'):
            players_visitor = self.db_worker.get_players(game['id'], game['id_visitor'])
            players_home = self.db_worker.get_players(game['id'], game['id_home'])

            is_b2b_visitor = self.is_b2b_game(game['id'], game['id_visitor'], game['date'])
            is_b2b_home = self.is_b2b_game(game['id'], game['id_home'], game['date'])
            is_win = self.is_win(game['pts_visitor'], game['pts_home'])

            list_per_visitor = self.process_players(players_visitor, 1)
            list_per_home = self.process_players(players_home, 2)

            game |= list_per_visitor
            game |= list_per_home
            game.update({'visitor_b2b': is_b2b_visitor})
            game.update({'home_b2b': is_b2b_home})
            game.update({'Y': is_win})
        return games

    def is_b2b_game(self, id_game, id_team, current_date):
        id_previous_game = self.get_previous_game(id_game, id_team)
        if id_previous_game is None:
            return 0

        previous_date = self.db_worker.get_field_by_value('games', 'date', 'id', id_previous_game)
        return self.is_b2b(current_date, previous_date['date'])

    def get_previous_game(self, id_game, id_team):
        games = self.db_worker.get_all_games_for_team(id_team)
        index = self.find(games, 'id_game', id_game)
        if index == 0:
            return None
        return games[index - 1]['id_game']

    @staticmethod
    def find(lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    @staticmethod
    def is_b2b(current_time, previous_time):
        if previous_time == '' or current_time == '':
            return 0

        current = int(current_time.split(',')[-2].split()[-1])
        previous = int(previous_time.split(',')[-2].split()[-1])
        return 1 if current - previous == 1 else 0

    @staticmethod
    def is_win(pts_visitor, pts_home):
        return 1 if pts_visitor > pts_home else 0

    def process_players(self, players, j):
        list_per = [self.get_per(player) for player in players]
        list_per.sort(key=lambda x: (x['per'] is not None, x['per']), reverse=True)
        return {f't{j}p{i}_per': item['per'] for i, item in enumerate(list_per[:8])}

    @staticmethod
    def get_per(player):
        time = player['mp'].split(':')
        # if len(time) == 1 and time[0] == '':
        #     return {'mp': None, 'per': None}

        m, s = time[0], time[1] if len(time) > 1 else 0
        time_value = round((int(m) * 60 + int(s)) / 60, 3)

        # stats_list = ['ft', 'fta', 'fg', 'fga', 'fg3', 'stl', 'blk', 'orb', 'ast', 'drb', 'tov', 'pf']
        # for stat in stats_list:
        #     if player[stat] is None:
        #         return {'mp': time_value, 'per': None}

        free_throw_miss = player['fta'] - player['ft']
        field_goal_miss = player['fga'] - player['fg']
        per = player['fg'] * 85.910 + player['stl'] * 53.897 + player['fg3'] * 51.757 + \
              player['ft'] * 46.845 + player['blk'] * 39.190 + player['orb'] * 39.190 + \
              player['ast'] * 34.677 + player['drb'] * 14.707 - player['pf'] * 17.174 - \
              free_throw_miss * 20.091 - field_goal_miss * 39.190 - player['tov'] * 53.897

        if time_value == 0:
            return {'mp': time_value, 'per': 0}
        per *= (1 / time_value)
        return {'mp': time_value, 'per': per}

    @staticmethod
    def to_df(data):
        return pd.DataFrame(data)

    def to_normalize_data(self, df):
        df_data = df.loc[:, 'ELO_visitor':'t2p7_per']
        df_info = df.loc[:, :'id_home']
        normalized = df.loc[:, 'visitor_b2b':'Y']

        for column in df_data:
            print(f'{column} normalizing')
            default_extreme_values = self.get_extreme_threshold(column, df_data)
            self.save_extreme_values_to_db(column, default_extreme_values)
            df_data[column] = self.to_normalize(df_data[column], default_extreme_values)
        return pd.concat([df_info, df_data, normalized], axis=1)

    def save_extreme_values_to_db(self, name, values):
        self.db_worker.save_extreme_values(name, values['min'], values['max'])

    def get_extreme_threshold(self, column, df):
        if 'per' in column:
            default_extreme_values = {'max': 45, 'min': -45}
        else:
            default_extreme_values = self.get_min_max(df[column])
            default_extreme_values = default_extreme_values.to_dict()
        return default_extreme_values

    @staticmethod
    def get_min_max(x):
        return pd.Series(index=['min', 'max'], data=[x.min(), x.max()])

    @staticmethod
    def to_normalize(column, y):
        for i, value in enumerate(column):
            if value < y['min']:
                column[i] = y['min']
            if value > y['max']:
                column[i] = y['max']
        return [round(2 * ((x - y['min']) / (y['max'] - y['min'])) - 1, 3) for x in column]

    @staticmethod
    def save_data(normalized):
        way = f'data/training_data/dataset_{date.today().day}_{date.today().month}_{date.today().year}.csv'
        normalized.to_csv(way, index=False, encoding='utf-8')
