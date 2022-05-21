import torch
import pandas as pd
from modules.models.logistic_regression import LogisticRegression
from modules.features_collector import FeatureCollector


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
            features = self.get_features(game)
            self.to_predict(features)
            print(1)

    @staticmethod
    def get_features(game):
        feature_collector = FeatureCollector(game['visitor'], game['home'], game['date'], True)
        data = feature_collector.main()
        data.update({'name_1': game['visitor'], 'name_2': game['home']})
        return data

    def to_predict(self, features):
        visitor = features.pop('name_1')
        home = features.pop('name_2')

        data = torch.FloatTensor([recs for recs in features.values()])
        prediction = self.model(data)
        print(f'{visitor} wins {home} with a {round(prediction.item(), 3)} percent chance')
