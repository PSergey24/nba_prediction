from __future__ import annotations
from typing import List
from .tools import BSTools
from .data import Game, Team, Player, ParsingStatus
from .elo_counter import EloCounter
from .setting import ScrapperSetting
from modules.db_worker import DBWorker


class GameScrapper:

    def __init__(self, game: Game, status: ParsingStatus):
        self.game = game
        self.status = status
        self.setting = ScrapperSetting()
        self.bs_tools = BSTools()
        self.elo_counter = EloCounter()
        self.db_worker = DBWorker('data/db/nba.db')

    def main(self):
        self.game.soup = self.bs_tools.get_soup(self.game.link)
        self.parse_data()
        self.update_elo_rating()
        print(f'Game #{self.status.game} {self.game.visitor_name} - {self.game.home_name} was parsed. Season {self.game.date}')

    def parse_data(self) -> None:
        self.get_teams_id()
        self.parse_info_about_game()
        self.parse_game_table()

    def get_teams_id(self):
        self.game.id_visitor = self.status.franchises[self.game.visitor_name]
        self.game.id_home = self.status.franchises[self.game.home_name]

    def parse_info_about_game(self) -> None:
        self.parse_header()
        self.parse_inactive()

    def parse_header(self) -> None:
        h1 = self.game.soup.find('h1')
        stage = h1.text.split(':')
        if len(stage) == 1:
            self.game.round = 'Regular Season'
        elif stage[0] == 'Play-In Game':
            self.game.round = 'Play-In Game'
        else:
            self.game.round = " ".join(stage[0].split(' ')[-4:-2])

    def parse_inactive(self) -> None:
        wrap = self.game.soup.find('div', id='all_box-' + self.game.home + '-game-advanced', class_="section_wrapper")
        inactive_box = wrap.nextSibling.nextSibling
        if inactive_box is not None:
            pos = inactive_box.text.find('Officials')
            text = inactive_box.text[:pos].split(self.game.home)
            if len(text) > 1:
                inactive_links = inactive_box.find('div').find_all('a')
                self.game.visitor_inactive = []
                self.game.home_inactive = []
                for a in inactive_links:
                    link = a.attrs['href'].split('/')[-1].replace('.html', '')
                    name = a.text.replace(' ', '_')
                    if a.text in text[0]:
                        self.game.visitor_inactive.append(link + '_' + name)
                    elif a.text in text[1]:
                        self.game.home_inactive.append(link + '_' + name)

    def parse_game_table(self) -> None:
        self.parse_game_table_players()
        self.parse_game_table_teams()

    def parse_game_table_players(self) -> None:
        self.game.visitor_roster = self.parse_players_info(self.game.visitor)
        self.game.home_roster = self.parse_players_info(self.game.home)

    def parse_game_table_teams(self) -> None:
        self.game.visitor_stats = self.parse_team_info(self.game.visitor)
        self.game.home_stats = self.parse_team_info(self.game.home)

    def parse_players_info(self, team_name: str) -> List[Player]:
        table_id = 'box-' + team_name + '-game-basic'
        tr_list = self.game.soup.find(id=table_id).find('tbody').find_all("tr", {'class': None})
        return self.get_all_stats(tr_list)

    def get_all_stats(self, rows):
        players = [self.get_item_stats(row) for row in rows]
        return [player for player in players if player is not None]

    def parse_team_info(self, team_name: str) -> Team:
        table_id = 'box-' + team_name + '-game-basic'
        total_row_soup = self.game.soup.find(id=table_id).find('tfoot').find("tr")
        return self.get_item_stats(total_row_soup, player=False)

    @staticmethod
    def get_item_stats(soup, player=True):
        if soup.find(attrs={"data-stat": "reason"}) is not None:
            return

        fg = int(soup.find(attrs={"data-stat": "fg"}).text)
        fga = int(soup.find(attrs={"data-stat": "fga"}).text)
        fg3 = int(soup.find(attrs={"data-stat": "fg3"}).text)
        fg3a = int(soup.find(attrs={"data-stat": "fg3a"}).text)
        ft = int(soup.find(attrs={"data-stat": "ft"}).text)
        fta = int(soup.find(attrs={"data-stat": "fta"}).text)
        orb = int(soup.find(attrs={"data-stat": "orb"}).text)
        drb = int(soup.find(attrs={"data-stat": "drb"}).text)
        ast = int(soup.find(attrs={"data-stat": "ast"}).text)
        stl = int(soup.find(attrs={"data-stat": "stl"}).text)
        blk = int(soup.find(attrs={"data-stat": "blk"}).text)
        tov = int(soup.find(attrs={"data-stat": "tov"}).text)
        pf = int(soup.find(attrs={"data-stat": "pf"}).text)
        pts = int(soup.find(attrs={"data-stat": "pts"}).text)

        if player is True:
            name = soup.find(attrs={"data-stat": "player"}).text
            link = soup.find(attrs={"data-stat": "player"}).find('a')['href']
            mp = soup.find(attrs={"data-stat": "mp"}).text
            return Player(name, mp, fg, fga, fg3, fg3a, ft, fta, orb, drb, ast, stl, blk, tov, pf, pts, link)
        return Team(fg, fga, fg3, fg3a, ft, fta, orb, drb, ast, stl, blk, tov, pf, pts)

    def update_elo_rating(self) -> None:
        id_visitor = self.game.id_visitor
        id_home = self.game.id_home

        visitor_new_elo = self.elo_counter.get_elo(self.status.current_elo[id_visitor],
                                                   self.status.current_elo[id_home], self.game.pts_visitor,
                                                   self.game.pts_home)

        home_new_elo = self.elo_counter.get_elo(self.status.current_elo[id_home],
                                                self.status.current_elo[id_visitor], self.game.pts_home,
                                                self.game.pts_visitor)

        self.update_elo(id_visitor, visitor_new_elo)
        self.update_elo(id_home, home_new_elo)
        self.game.home_stats.elo = home_new_elo
        self.game.visitor_stats.elo = visitor_new_elo

    def update_elo(self, id_team, new_elo):
        self.status.current_elo.update({id_team: new_elo})
        self.db_worker.update_elo(id_team, new_elo)