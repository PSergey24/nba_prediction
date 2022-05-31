import time
from dataclasses import asdict
from typing import List
from modules.db_worker import DBWorker
from .game_scrapper import GameScrapper
from .tools import BSTools
from .data import Season, Game, ParsingStatus


class SeasonScrapper:

    def __init__(self, season: Season, status: ParsingStatus):
        self.season = season
        self.status = status
        self.game_scrapper = None
        self.bs_tools = BSTools()
        self.db_worker = DBWorker('data/db/nba.db')

    def main(self) -> None:
        self.season.soup = self.bs_tools.get_soup(self.season.link)
        self.parse_data()
        self.process_games()
        print(f'Season was parsed and processed: {self.status.season}')

    def parse_data(self) -> None:
        self.parse_list_months()
        self.parse_list_games()

    def parse_list_months(self) -> None:
        month_block = self.season.soup.find('div', class_='filter')
        month_list = month_block.find_all('a')
        self.season.months = ['https://www.basketball-reference.com' + month['href'] for month in month_list]

    def parse_list_games(self) -> None:
        games_list = self.get_list_games()
        self.season.games = [item for item in games_list if item.link is not None]

    def get_list_games(self) -> List[Game]:
        return [item for month in self.season.months for item in self.process_month(month)]

    def process_month(self, month: str) -> List[Game]:
        soup_month = self.bs_tools.get_soup(month)
        rows = soup_month.find('tbody').find_all("tr", {'class': None})
        games_list = [self.process_table_row(row) for row in rows]
        return games_list

    @staticmethod
    def process_table_row(row):
        a = row.find("td", {"data-stat": "box_score_text"}).find('a')
        link = None if a is None else 'https://www.basketball-reference.com' + a['href']
        date = row.find(attrs={"data-stat": "date_game"}).text
        visitor = row.find(attrs={"data-stat": "visitor_team_name"}).find('a')['href'].split('/')[-2]
        visitor_name = row.find(attrs={"data-stat": "visitor_team_name"}).find('a').text
        visitor_pts = row.find(attrs={"data-stat": "visitor_pts"}).text
        home = row.find(attrs={"data-stat": "home_team_name"}).find('a')['href'].split('/')[-2]
        home_name = row.find(attrs={"data-stat": "home_team_name"}).find('a').text
        home_pts = row.find(attrs={"data-stat": "home_pts"}).text
        arena = row.find(attrs={"data-stat": "arena_name"}).text
        if link is None:
            return Game(date, visitor_name, visitor, visitor_pts, home_name, home,
                        home_pts, arena, link)
        return Game(date, visitor_name, visitor, int(visitor_pts), home_name, home,
                    int(home_pts), arena, link)

    def process_games(self) -> None:
        for i in range(self.status.game, len(self.season.games)):
            game = self.season.games[i]
            self.process_game(game)
            self.save_data_to_db()
            self.update_status()
            time.sleep(2)

    def process_game(self, game: Game) -> None:
        self.game_scrapper = GameScrapper(game, self.status)
        self.game_scrapper.main()

    def save_data_to_db(self):
        id_game = self.save_games_to_db()
        self.save_players_to_db(id_game)
        self.save_games_teams_to_db(id_game)

    def save_games_to_db(self):
        self.game_scrapper.game.soup = None
        games = asdict(self.game_scrapper.game)
        games = self.pop_keys(games, ['arena', 'home', 'home_inactive', 'home_name', 'home_stats',
                                      'home_roster', 'visitor', 'visitor_inactive', 'visitor_name', 'visitor_stats',
                                      'visitor_roster', 'soup'])
        games.update({'season': self.status.season})
        columns = ', '.join(games.keys())
        values = [int(x) if isinstance(x, bool) else x for x in games.values()]
        self.db_worker.insert('games', columns, values)
        id_game = self.db_worker.get_game_id()
        return id_game

    def save_players_to_db(self, id_game):
        self.save_team_players_to_db(self.game_scrapper.game.home_roster, id_game, self.game_scrapper.game.id_home)
        self.save_team_players_to_db(self.game_scrapper.game.visitor_roster, id_game, self.game_scrapper.game.id_visitor)

    def save_team_players_to_db(self, players, id_game, id_team):
        [self.save_player_to_db(player, id_game, id_team) for player in players]

    def save_player_to_db(self, player, id_game, id_team):
        self.db_worker.update_player(player.name, player.link)
        id_player = self.db_worker.get_player_id(player.link)
        player_dict = asdict(player)
        player_dict = self.pop_keys(player_dict, ['link', 'name'])
        player_dict.update({'id_game': id_game, 'id_player': id_player, 'id_team': id_team})
        columns = ', '.join(player_dict.keys())
        values = [int(x) if isinstance(x, bool) else x for x in player_dict.values()]
        self.db_worker.insert('games_players', columns, values)

    def save_games_teams_to_db(self, id_game):
        id_visitor = self.game_scrapper.game.id_visitor
        id_home = self.game_scrapper.game.id_home
        elo_visitor = self.game_scrapper.game.visitor_stats.elo
        elo_home = self.game_scrapper.game.home_stats.elo

        self.db_worker.update_game_team(id_game, id_visitor, elo_visitor)
        self.db_worker.update_game_team(id_game, id_home, elo_home)

    @staticmethod
    def pop_keys(input_dict, keys_to_remove) -> dict:
        result = {}
        for key in keys_to_remove:
            result.update({key: input_dict})
            input_dict.pop(key)
        return input_dict

    def update_status(self) -> None:
        self.status.game += 1
        self.db_worker.update_game_index(self.status.season, self.status.game)
