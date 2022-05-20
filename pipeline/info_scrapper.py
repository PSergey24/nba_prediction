import time
from datetime import datetime
from modules.data_scrapper import RosterScrapper, ScheduleScrapper


class Helper:

    @staticmethod
    def main():
        roster_scrapper = RosterScrapper()
        schedule_scrapper = ScheduleScrapper()

        while True:
            roster_scrapper.main()
            schedule_scrapper.main()

            now = datetime.now()
            print(f"Rosters and schedule were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(20)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
