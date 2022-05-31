import time
from datetime import datetime
from modules.game_predictor import GamePredictor


class Helper:

    def __init__(self):
        # every 0.5 days
        self.period = 43200

    def main(self):
        print(f"Game Predictor started work (update every 10 days)")
        time.sleep(self.period)
        predictor = GamePredictor()

        while True:
            predictor.main()

            now = datetime.now()
            print(f"Game predictor made prediction, {now.strftime('%H:%M:%S')}")
            time.sleep(self.period)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
