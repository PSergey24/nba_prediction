import time
from datetime import datetime
from modules.features_collector import FeatureCollectorDB


class Helper:

    def __init__(self):
        # every 5 days
        self.period = 432000

    def main(self):
        print(f"Feature's updater started work (update every 5 days)")
        time.sleep(self.period)
        updater = FeatureCollectorDB()

        while True:
            updater.main()

            now = datetime.now()
            print(f"Features were updated, {now.strftime('%H:%M:%S')}")
            time.sleep(self.period)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
