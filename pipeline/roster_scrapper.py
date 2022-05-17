import time
from datetime import datetime
from modules.data_scrapper import RosterScrapper


class Helper:

    @staticmethod
    def main():
        roster_scrapper = RosterScrapper()

        while True:
            roster_scrapper.update()

            now = datetime.now()
            print(f"Rosters were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(20)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
