import os
import datetime as dt
from modules.data_cleaner import DataCleaner
from modules.data_handler.data_normalizer import DataNormalizer


class Checker:

    def main(self):
        teams_list = self.get_updated_files('data/raw_data/teams')
        players_list = self.get_updated_files('data/raw_data/players')

        data_cleaner = DataCleaner(players_list, teams_list)
        data_cleaner.main()

        data_normalizer = DataNormalizer(players_list, teams_list)
        data_normalizer.to_normalize_data()

    @staticmethod
    def get_updated_files(directory):
        now = dt.datetime.now()
        ago = now - dt.timedelta(minutes=120)

        results = []

        files = [name for name in os.listdir(directory) if '.csv' in name]
        for fname in files:
            path = os.path.join(directory, fname)
            st = os.stat(path)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > ago:
                results.append(path.split('/')[-1])
        return results
