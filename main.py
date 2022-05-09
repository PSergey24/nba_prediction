from modules.data_scrapper import DataScrapper
from modules.data_cleaner import DataCleaner
from modules.data_normalizer.data_normalizer import DataNormalizer


if __name__ == '__main__':
    data_scrapper = DataScrapper()
    data_cleaner = DataCleaner()
    data_normalizer = DataNormalizer()

    # data_scrapper.main()
    # data_cleaner.main()
    data_normalizer.get_stats()
