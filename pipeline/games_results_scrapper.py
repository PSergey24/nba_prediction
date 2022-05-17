import time
from datetime import datetime
from modules.data_scrapper import DataScrapper


class Helper:

    @staticmethod
    def main():
        data_scrapper = DataScrapper()

        while True:
            data_scrapper.main()

            now = datetime.now()
            print(f"Game's results were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(40)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
