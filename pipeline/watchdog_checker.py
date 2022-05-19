import time
from datetime import datetime
from modules.watchdog_checker import Checker


class Helper:

    @staticmethod
    def main():
        checker = Checker()

        while True:
            checker.main()

            now = datetime.now()
            print(f"Recently updated files have been checked, {now.strftime('%H:%M:%S')}")
            time.sleep(30)


if __name__ == '__main__':
    helper = Helper()
    helper.main()
