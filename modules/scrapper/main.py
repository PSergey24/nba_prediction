from datetime import datetime
from .season_scrapper import SeasonScrapper
from modules.db_worker import DBWorker
from .data import Season, ParsingStatus


class Scrapper:

    def __init__(self):
        self.status = ParsingStatus(2022, 0)
        self.season_scrapper = None
        self.seasons_list = None
        self.db_worker = DBWorker('data/db/nba.db')

        self.status.current_elo = {}
        self.status.franchises = {}

    def main(self):
        self.get_status()
        self.get_seasons()
        self.process_seasons()
        self.db_worker.conn.close()

    def get_status(self, is_start=False) -> None:
        if is_start is True:
            self.reset_status()
        else:
            self.get_current_status()
        self.get_franchises()

    def get_franchises(self):
        rows = self.db_worker.get_all('franchises')
        rows = self.correct_franchises_name(rows)
        [self.status.franchises.update({row[2]: row[1]}) for row in rows]

    @staticmethod
    def correct_franchises_name(rows):
        names = {'NO/Ok. City Hornets': 'New Orleans/Oklahoma City Hornets'}
        for i, row in enumerate(rows):
            if row[2] in names:
                row = list(row)
                row[2] = names[row[2]]
                rows[i] = tuple(row)
        return rows

    def reset_status(self):
        self.reset_elo()
        self.reset_season()

    def reset_elo(self):
        for id_team in range(1, 31):
            sql = 'REPLACE INTO ELO (id_team, ELO) VALUES ({}, 1500)'.format(id_team)
            self.db_worker.conn.execute(sql)
            self.db_worker.conn.commit()
            self.status.current_elo.update({id_team: 1500})

    def reset_season(self):
        sql = 'REPLACE INTO CURRENT_PROCESS (id, season, game) VALUES (1, {}, 0)'.format(self.status.season)
        self.db_worker.conn.execute(sql)
        self.db_worker.conn.commit()

    def get_current_status(self):
        self.get_current_elo()
        self.get_current_season()

    def get_current_elo(self):
        sql = 'SELECT * FROM {}'.format('ELO')
        rows = self.db_worker.conn.execute(sql).fetchall()
        [self.status.current_elo.update({row[1]: row[2]}) for row in rows]

    def get_current_season(self):
        sql = 'SELECT * FROM {}'.format('CURRENT_PROCESS')
        rows = self.db_worker.conn.execute(sql).fetchall()
        self.status.season = rows[0][1]
        self.status.game = rows[0][2]

    def get_seasons(self) -> None:
        if self.seasons_list is None:
            self.seasons_list = ['https://www.basketball-reference.com/leagues/NBA_' + str(season) + '_games.html' for
                                 season in range(self.status.season, int(datetime.now().year + 1))]

    def process_seasons(self) -> None:
        for season in self.seasons_list:
            self.process_season(season)
            self.update_status()

    def process_season(self, link: str) -> None:
        season = Season(link)
        self.season_scrapper = SeasonScrapper(season, self.status)
        self.season_scrapper.main()

    def update_status(self):
        self.update_elo_after_season()
        self.update_season_game()

    def update_elo_after_season(self) -> None:
        self.update_status_elo()

    def update_status_elo(self) -> None:
        for key, value in self.status.current_elo.items():
            new_rating = (value * 0.75) + (1505 * 0.25)
            self.status.current_elo.update({key: new_rating})
            self.db_worker.update_elo(key, new_rating)

    def update_season_game(self):
        self.status.season += 1
        self.status.game = 0
        self.db_worker.update_game_index(self.status.season, self.status.game)
