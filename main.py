from modules.models.logistic_regression import Trainer
from modules.game_predictor import GamePredictor
from modules.scrapper import Scrapper, ScheduleScrapper, RosterScrapper
from modules.features_collector import FeatureCollectorDB


if __name__ == '__main__':
    # schedule_scrapper = ScheduleScrapper()
    # schedule_scrapper.main()

    # roster_scrapper = RosterScrapper()
    # roster_scrapper.main()

    # trainer = Trainer()
    # trainer.main()

    # game_predictor = GamePredictor()
    # game_predictor.main()

    # feature_collector = FeatureCollectorDB()
    # feature_collector.main()

    scrapper = Scrapper()
    scrapper.main()





