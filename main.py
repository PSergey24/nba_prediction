from modules.data_scrapper import DataScrapper
from modules.data_cleaner import DataCleaner
from modules.data_handler.data_normalizer import DataNormalizer
from modules.data_handler.data_collector import DataCollector


if __name__ == '__main__':
    data_scrapper = DataScrapper()
    data_cleaner = DataCleaner()
    data_normalizer = DataNormalizer()
    data_collector = DataCollector()

    # data_scrapper.main()
    # data_cleaner.main()
    # data_handler.save_min_max_stats()
    # data_normalizer.to_normalize_data()
    data_collector.main()
