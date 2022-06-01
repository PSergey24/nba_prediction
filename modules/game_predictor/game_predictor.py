import torch
from datetime import datetime
from pytz import timezone
from time import strptime
from modules.models.logistic_regression import LogisticRegression
from modules.features_collector import FeatureCollectorDB
from modules.telegram_bot import TelegramBot
from modules.db_worker import DBWorker


class GamePredictor:

    def __init__(self):
        self.model = LogisticRegression(20, 264, 1)
        self.games = None
        self.db_worker = DBWorker('data/db/nba.db')
        self.tg_bot = TelegramBot()

    def main(self):
        games = self.get_schedule()
        self.get_weights()
        self.process_games(games)
        self.db_worker.conn.close()

    def get_schedule(self):
        games = self.db_worker.get_all('SCHEDULE')
        games = self.to_filter_games(games)
        return games

    def to_filter_games(self, games):
        tz = timezone('EST')
        current_time = datetime.now(tz)

        filtered_games = []
        for game in reversed(games):
            year, month, day, hour = self.get_game_start_time(game[3])
            if month == current_time.month and day == current_time.day and abs(hour - current_time.hour) < 4:
                filtered_games.append(game)
            if month != current_time.month or day != current_time.day:
                return filtered_games
        return filtered_games

    @staticmethod
    def get_game_start_time(time_db):
        list_time = time_db.split(',')
        if len(list_time) == 4:
            hour = int(list_time[0].split(':')[0])
            month = int(strptime(list_time[2].strip().split(' ')[0], '%b').tm_mon)
            day = int(list_time[2].strip().split(' ')[1])
            year = int(list_time[3].strip())
            return year, month, day, hour
        elif len(list_time) == 4:
            hour = None
            month = int(strptime(list_time[1].strip().split(' ')[0], '%b').tm_mon)
            day = int(list_time[1].strip().split(' ')[1])
            year = int(list_time[2].strip())
            return year, month, day, hour

    def get_weights(self):
        models = self.db_worker.get_all('models')
        model = self.get_the_better_model(models)
        self.model.load_state_dict(torch.load(model[3]))
        self.model.eval()

    @staticmethod
    def get_the_better_model(models):
        models.sort(key=lambda x: x[2], reverse=True)
        models = [model for model in models if model[1] == 'logistic_regression']
        return models[0]

    def process_games(self, games):
        for game in games:
            features = self.get_features(game)
            normalized = self.to_normalize_features(features)
            self.to_predict(normalized, game)

    @staticmethod
    def get_features(game):
        feature_collector = FeatureCollectorDB()
        data = feature_collector.prediction(game[1], game[2], game[3])
        return data

    def to_normalize_features(self, features):
        normalized = {}
        min_max = self.db_worker.get_all('min_max')
        for feature, value in features.items():
            extreme_values = self.get_extreme_values(min_max, feature)
            if feature in ['visitor_b2b', 'home_b2b']:
                normalized_value = value
            else:
                normalized_value = self.to_normalize(value, extreme_values[0])
            normalized.update({feature: normalized_value})
        return normalized

    @staticmethod
    def get_extreme_values(min_max, feature):
        return [item for item in min_max if item[1] == feature]

    @staticmethod
    def to_normalize(value, extreme_values):
        min_value = extreme_values[2]
        max_value = extreme_values[3]
        n_value = round(2 * ((value - min_value) / (max_value - min_value)) - 1, 3)
        return n_value

    def to_predict(self, features, game):
        data = torch.FloatTensor([recs for recs in features.values()])
        prediction = self.model(data)
        message = f"{game[3]} | {game[1]} wins {game[2]} with a {round(prediction.item(), 3)} percent chance"
        self.tg_bot.send_message(message)
        print(message)
