--DROP TABLE IF EXISTS franchises;
--
--CREATE TABLE franchises (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    id_franchise INTEGER NOT NULL,
--    name TEXT NOT NULL,
--    lg TEXT NOT NULL,
--    first_season INTEGER NOT NULL,
--    last_season INTEGER NOT NULL
--);

DROP TABLE IF EXISTS players;

CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    link TEXT type UNIQUE
);

DROP TABLE IF EXISTS games;

CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    'date' TEXT NOT NULL,
    season INTEGER NOT NULL,
    round TEXT NOT NULL,
    id_visitor INTEGER NOT NULL,
    pts_visitor INTEGER NOT NULL,
    id_home INTEGER NOT NULL,
    pts_home INTEGER NOT NULL,
    link TEXT NOT NULL,
    FOREIGN KEY (id_visitor)
       REFERENCES franchises (id_franchise),
    FOREIGN KEY (id_home)
       REFERENCES franchises (id_franchise)
);


DROP TABLE IF EXISTS games_teams;

CREATE TABLE games_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_game INTEGER NOT NULL,
    id_team INTEGER NOT NULL,
    ELO REAL NOT NULL,
    FOREIGN KEY (id_game)
       REFERENCES games (id),
    FOREIGN KEY (id_team)
       REFERENCES franchises (id_franchise)
);


DROP TABLE IF EXISTS games_players;

CREATE TABLE games_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_game INTEGER NOT NULL,
    id_player INTEGER NOT NULL,
    id_team INTEGER NOT NULL,
    mp TEXT NOT NULL,
    fg INTEGER NOT NULL,
    fga INTEGER NOT NULL,
    fg3 INTEGER NOT NULL,
    fg3a INTEGER NOT NULL,
    ft INTEGER NOT NULL,
    fta INTEGER NOT NULL,
    orb INTEGER NOT NULL,
    drb INTEGER NOT NULL,
    ast INTEGER NOT NULL,
    stl INTEGER NOT NULL,
    blk INTEGER NOT NULL,
    tov INTEGER NOT NULL,
    pf INTEGER NOT NULL,
    pts INTEGER NOT NULL,
    FOREIGN KEY (id_game)
       REFERENCES games (id),
    FOREIGN KEY (id_player)
       REFERENCES players (id)
);


DROP TABLE IF EXISTS rosters;

CREATE TABLE rosters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_team INTEGER NOT NULL,
    id_player INTEGER NOT NULL,
    FOREIGN KEY (id_team)
       REFERENCES franchises (id_franchise),
    FOREIGN KEY (id_player)
       REFERENCES players (id)
);

DROP TABLE IF EXISTS ELO;

CREATE TABLE ELO (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_team INTEGER type UNIQUE,
    ELO REAL NOT NULL,
    FOREIGN KEY (id_team)
       REFERENCES franchises (id_franchise)
);

DROP TABLE IF EXISTS SCHEDULE;

CREATE TABLE SCHEDULE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor INTEGER NOT NULL,
    home INTEGER NOT NULL,
    'date' TEXT NOT NULL,
    FOREIGN KEY (visitor)
       REFERENCES franchises (id_franchise),
    FOREIGN KEY (home)
       REFERENCES franchises (id_franchise)
);

DROP TABLE IF EXISTS CURRENT_PROCESS;

CREATE TABLE CURRENT_PROCESS (
    id INTEGER type UNIQUE,
    season INTEGER NOT NULL,
    game INTEGER NOT NULL
);

DROP TABLE IF EXISTS models;

CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    accuracy REAL NOT NULL,
    way_to_model TEXT type UNIQUE,
    way_to_dataset TEXT type UNIQUE
);

DROP TABLE IF EXISTS min_max;

CREATE TABLE min_max (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT type UNIQUE,
    min_value REAL NOT NULL,
    max_value REAL NOT NULL
);