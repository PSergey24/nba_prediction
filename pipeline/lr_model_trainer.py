import time
from datetime import datetime
from modules.models.logistic_regression import Trainer


class Helper:

    def __init__(self):
        # every 10 days
        self.period = 864000

    def main(self):
        print(f"LR Trainer started work (update every 10 days)")
        time.sleep(self.period)
        trainer = Trainer()

        while True:
            trainer.main()

            now = datetime.now()
            print(f"LR trainer was updated, {now.strftime('%H:%M:%S')}")
            time.sleep(self.period)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
