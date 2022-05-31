import time
from datetime import datetime
from modules.scrapper import ScheduleScrapper, RosterScrapper


class Helper:

    def __init__(self):
        # every day
        self.period = 86400

    def main(self):
        print(f"Roster's and schedule's updater started work (update every {self.period} seconds)")
        time.sleep(self.period)
        roster_scrapper = RosterScrapper()
        schedule_scrapper = ScheduleScrapper()

        while True:
            roster_scrapper.main()
            schedule_scrapper.main()

            now = datetime.now()
            print(f"Rosters and schedule were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(self.period)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
