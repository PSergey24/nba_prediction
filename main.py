from modules.data_scrapper import DataScrapper, RosterScrapper, ScheduleScrapper
from modules.data_cleaner import DataCleaner
from modules.data_handler.data_normalizer import DataNormalizer
from modules.data_handler.data_collector import DataCollector
from modules.models.logistic_regression import Trainer
from modules.watchdog_checker import Checker
from modules.game_predictor import GamePredictor


if __name__ == '__main__':
    data_scrapper = DataScrapper()
    roster_scrapper = RosterScrapper()
    schedule_scrapper = ScheduleScrapper()
    data_cleaner = DataCleaner()
    data_normalizer = DataNormalizer()
    data_collector = DataCollector()
    trainer = Trainer()
    game_predictor = GamePredictor()

    # data_scrapper.main()
    # roster_scrapper.main()
    # schedule_scrapper.main()

    # data_cleaner.main()
    # data_normalizer.save_min_max_stats()
    # data_normalizer.to_normalize_data()

    # file_checker = Checker()
    # file_checker.main()

    # data_collector.main()
    # trainer.train()
    game_predictor.main()


