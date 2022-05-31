import time
from datetime import datetime
from modules.scrapper import Scrapper


class Helper:

    def __init__(self):
        # every half day
        self.period = 43200

    def main(self):
        print(f"Game's updater started work (update every {self.period} seconds)")
        # time.sleep(self.period)
        data_scrapper = Scrapper()

        while True:
            data_scrapper.main()

            now = datetime.now()
            print(f"Game's results were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(self.period)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
