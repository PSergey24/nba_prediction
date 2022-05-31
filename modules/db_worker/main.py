import sqlite3


class DBWorker:

    def __init__(self, db):
        self.conn = sqlite3.connect(db)

    @staticmethod
    def dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def get_all(self, table_name):
        sql = 'SELECT * FROM {}'.format(table_name)
        rows = self.conn.execute(sql).fetchall()
        return rows

    def get_field_by_value(self, table, field, condition_field, condition_value):
        self.conn.row_factory = self.dict_factory
        sql = 'SELECT {} FROM {} WHERE {}={}'.format(field, table, condition_field, condition_value)
        rows = self.conn.execute(sql).fetchall()
        return rows[0]

    def insert(self, table_name, columns, values):
        placeholders = ', '.join('?' * len(values))
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, columns, placeholders)
        self.conn.execute(sql, values)
        self.conn.commit()

    def clear_table(self, table_name):
        sql = 'DELETE FROM {}'.format(table_name)
        self.conn.execute(sql)
        self.conn.commit()

    def reset_ai(self, table_name):
        sql = 'UPDATE SQLITE_SEQUENCE SET seq=0 WHERE name="{}"'.format(table_name)
        self.conn.execute(sql)
        self.conn.commit()

    # --- scrapper/main.py ---

    # --- season_scrapper.py ---
    # to increase game's index that was processed
    def update_game_index(self, season, game):
        sql = 'REPLACE INTO CURRENT_PROCESS (id, season, game) VALUES (1, {}, {})'.format(season, game)
        self.conn.execute(sql)
        self.conn.commit()

    def update_player(self, name, link):
        sql = 'INSERT OR IGNORE INTO players (name, link) VALUES ("{}", "{}")'.format(name, link)
        self.conn.execute(sql)
        self.conn.commit()

    def get_game_id(self):
        sql = 'SELECT id FROM games ORDER BY ID DESC LIMIT 1'
        rows = self.conn.execute(sql).fetchall()
        return rows[0][0]

    def get_player_id(self, link):
        sql = 'SELECT id FROM players WHERE link="{}"'.format(link)
        rows = self.conn.execute(sql).fetchall()
        if len(rows) == 0:
            return None
        return rows[0][0]

    def update_game_team(self, id_game, id_team, elo):
        sql = 'INSERT INTO games_teams (id_game, id_team, ELO) VALUES ({}, {}, {})'.format(id_game, id_team, elo)
        self.conn.execute(sql)
        self.conn.commit()

    # --- game_scrapper.py ---
    def update_elo(self, id_team, elo):
        sql = 'REPLACE INTO ELO (id_team, ELO) VALUES ({}, {})'.format(id_team, elo)
        self.conn.execute(sql)
        self.conn.commit()

    # --- scrapper/roster_scrapper.py ---
    def insert_new_player(self, name, link):
        sql = 'INSERT INTO players (name, link) VALUES ("{}", "{}")'.format(name, link)
        self.conn.execute(sql)
        self.conn.commit()

    def get_team_id(self, name):
        sql = 'SELECT id_franchise FROM franchises WHERE name="{}"'.format(name)
        rows = self.conn.execute(sql).fetchall()
        if len(rows) == 0:
            return None
        return rows[0][0]

    # --- models ---
    def insert_new_model(self, name, accuracy, way_to_model, way_to_dataset):
        sql = 'REPLACE INTO models (name, accuracy, way_to_model, way_to_dataset) VALUES ("{}", "{}", "{}", "{}")'.format(name, accuracy, way_to_model, way_to_dataset)
        self.conn.execute(sql)
        self.conn.commit()

    # --- modules/features_collector ---
    def get_all_games(self):
        self.conn.row_factory = self.dict_factory
        sql = """SELECT g.id, g.link, g.date, g.season, g.pts_visitor, g.pts_home,  
                g.id_visitor, g.id_home, visitor.ELO_previous as 'ELO_visitor', 
                home.ELO_previous as 'ELO_home'
                FROM games g, 
                    (
                        SELECT id_game, id_team,
                        LAG (ELO) OVER(PARTITION BY id_team ORDER BY id) as 'ELO_previous'
                        FROM games_teams
                    ) as visitor, 
                    (
                        SELECT id_game, id_team,
                        LAG (ELO) OVER(PARTITION BY id_team ORDER BY id) as 'ELO_previous'
                        FROM games_teams
                    ) as home
                WHERE visitor.id_game=g.id AND visitor.id_team=g.id_visitor
                AND home.id_game=g.id AND home.id_team=g.id_home
                ORDER by g.id
                """
        rows = self.conn.execute(sql).fetchall()
        return rows

    def get_all_games_for_team(self, id_team):
        self.conn.row_factory = self.dict_factory
        sql = """SELECT * FROM games_teams WHERE id_team={}""".format(id_team)
        rows = self.conn.execute(sql).fetchall()
        return rows

    def save_extreme_values(self, name, min_value, max_value):
        sql = 'REPLACE INTO min_max (name, min_value, max_value) VALUES ("{}", "{}", "{}")'.format(
            name, min_value, max_value)
        self.conn.execute(sql)
        self.conn.commit()

    def get_players(self, id_game, id_team):
        self.conn.row_factory = self.dict_factory
        sql = """
                SELECT g.date, sub.id_player, sub.mp, sub.fg, sub.fga, sub.fg3, sub.fg3a, sub.ft, sub.fta, sub.orb, 
                sub.drb, sub.ast, sub.stl, sub.blk, sub.tov, sub.pf
                FROM games g, (
                                SELECT gp.id_player, gp.id_game, gp.mp,
                                    AVG(gp.fg) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'fg',
                                    AVG(gp.fga) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'fga',
                                    AVG(gp.fg3) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'fg3',
                                    AVG(gp.fg3a) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'fg3a',
                                    AVG(gp.ft) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'ft',
                                    AVG(gp.fta) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'fta',
                                    AVG(gp.orb) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'orb',
                                    AVG(gp.drb) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'drb',
                                    AVG(gp.ast) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'ast',
                                    AVG(gp.stl) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'stl',
                                    AVG(gp.blk) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'blk',
                                    AVG(gp.tov) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'tov',
                                    AVG(gp.pf) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and 1 PRECEDING) AS 'pf'
                                FROM games_players gp
                                WHERE gp.id_team={}
                                ) as sub
                WHERE sub.id_game=g.id AND g.id={}
        """.format(id_team, id_game)
        rows = self.conn.execute(sql).fetchall()
        return rows

    def get_last_game(self, name):
        self.conn.row_factory = self.dict_factory
        sql = """SELECT g.date, g.link, f.id_franchise, gt.ELO
                        FROM franchises f, games_teams gt, games g
                        WHERE f.name="{}" AND gt.id_team=f.id_franchise AND gt.id_game=g.id
                        ORDER BY g.id desc
                        LIMIT 1
                        """.format(name)
        rows = self.conn.execute(sql).fetchall()
        if len(rows) == 0:
            return None
        return rows[0]

    def get_active_players(self, id_team):
        self.conn.row_factory = self.dict_factory
        sql = """SELECT sub.mp, sub.fg, sub.fga, sub.fg3, sub.fg3a, sub.ft, sub.fta, sub.orb, 
                sub.drb, sub.ast, sub.stl, sub.blk, sub.tov, sub.pf
                FROM games g, (SELECT g.id, gt.id_team, gt.id_game
                                FROM games_teams gt, games g
                                WHERE gt.id_team={} AND gt.id_game=g.id
                                ORDER BY g.id desc
                                LIMIT 1
                                ) sub2,
                                (SELECT gp.id_player, gp.id_game, gp.id_team, gp.mp,
                                    AVG(gp.fg) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'fg',
                                    AVG(gp.fga) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'fga',
                                    AVG(gp.fg3) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'fg3',
                                    AVG(gp.fg3a) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'fg3a',
                                    AVG(gp.ft) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'ft',
                                    AVG(gp.fta) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'fta',
                                    AVG(gp.orb) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'orb',
                                    AVG(gp.drb) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'drb',
                                    AVG(gp.ast) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'ast',
                                    AVG(gp.stl) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'stl',
                                    AVG(gp.blk) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'blk',
                                    AVG(gp.tov) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'tov',
                                    AVG(gp.pf) OVER (Partition BY gp.id_player ROWS BETWEEN 10 PRECEDING and CURRENT ROW) AS 'pf'
                                FROM games_players gp
                                ) as sub
                WHERE sub2.id=g.id AND sub.id_game=g.id AND sub.id_team={}
                """.format(id_team, id_team)
        rows = self.conn.execute(sql).fetchall()
        if len(rows) == 0:
            return None
        return rows

    # --- modules/web/ ---
    def get_active_franchises(self):
        sql = 'SELECT * FROM franchises GROUP BY id_franchise HAVING MAX(last_season)'
        rows = self.conn.execute(sql).fetchall()
        return rows

    def get_games_by_team(self, id_team):
        self.conn.row_factory = self.dict_factory
        sql = """SELECT gt.ELO, g.date, g.pts_visitor, g.pts_home, g.link, SUM(gp.fg) AS 'fg', SUM(gp.fga) AS 'fga',
        SUM(gp.fg3) AS 'fg3', SUM(gp.fg3a) AS 'fg3a', SUM(gp.ft) AS 'ft', SUM(gp.fta) AS 'fta', SUM(gp.orb) AS 'orb',
        SUM(gp.drb) AS 'drb', SUM(gp.ast) AS 'ast', SUM(gp.stl) AS 'stl', SUM(gp.blk) AS 'blk', SUM(gp.tov) AS 'tov',
        SUM(gp.pf) AS 'pf', SUM(gp.pts) AS 'pts', f_visitor.name AS 'visitor', f_home.name AS 'home'
        FROM games_teams gt, games g, games_players gp, franchises f_home, franchises f_visitor
                        WHERE gt.id_team={} AND gt.id_game=g.id AND gt.id_team=gp.id_team AND gt.id_game=gp.id_game
                        AND f_visitor.id_franchise=g.id_visitor AND g.season BETWEEN f_visitor.first_season AND f_visitor.last_season
                        AND f_home.id_franchise=g.id_home AND g.season BETWEEN f_home.first_season AND f_home.last_season
                        GROUP BY(gt.id_game)
                        """.format(id_team)
        rows = self.conn.execute(sql).fetchall()
        return rows

