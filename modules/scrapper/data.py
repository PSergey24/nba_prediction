from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List


@dataclass
class Season:
    link: str
    games: List = None
    soup: BeautifulSoup = None
    months: List = None


@dataclass
class Player:
    name: str
    mp: str
    fg: int
    fga: int
    fg3: int
    fg3a: int
    ft: int
    fta: int
    orb: int
    drb: int
    trb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    pts: int
    link: str


@dataclass
class Team:
    fg: int
    fga: int
    fg3: int
    fg3a: int
    ft: int
    fta: int
    orb: int
    drb: int
    trb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    pts: int
    elo: float = None


@dataclass
class Game:
    date: str
    visitor_name: str
    visitor: str
    pts_visitor: int
    home_name: str
    home: str
    pts_home: int
    attendance: str
    arena: str
    link: str
    id_visitor: int = None
    visitor_stats: Team = None
    id_home: int = None
    home_stats: Team = None
    round: str = None
    visitor_roster: dict = None
    home_roster: dict = None
    visitor_inactive: list = None
    home_inactive: list = None
    soup: BeautifulSoup = None


@dataclass
class ParsingStatus:
    season: int
    game: int
    current_elo: dict = None
    franchises: dict = None
