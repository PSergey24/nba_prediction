from datetime import datetime
from .setting import ScrapperSetting
from .tools import BSTools
from modules.db_worker import DBWorker


class RosterScrapper:

    def __init__(self):
        self.bs_tools = BSTools()
        self.db_worker = DBWorker('data/db/nba.db')

    def main(self):
        links = self.get_links()
        self.clear_table()
        self.process_teams(links)
        self.db_worker.conn.close()

    def get_links(self):
        soup = self.bs_tools.get_soup('https://www.basketball-reference.com/teams/')
        a = soup.find('div', id='all_teams_active').find_all('a')
        return ['https://www.basketball-reference.com/teams/' + ScrapperSetting.TEAMS[item.text.lower()] + '/' + str(datetime.now().year) + '.html' for item in a]

    def clear_table(self):
        self.db_worker.clear_table('rosters')
        self.db_worker.reset_ai('rosters')

    def process_teams(self, links):
        [self.process_team(link) for link in links]

    def process_team(self, link):
        soup = self.bs_tools.get_soup(link)
        players_containers = soup.find('div', id='div_roster').find_all("td", {"data-stat": "player"})
        players = self.get_players(players_containers)
        team_name = self.get_team_name(soup)
        team_id = self.get_team_id(team_name)
        self.insert_roster_to_db(players, team_id)

    def get_players(self, players_containers):
        players = []
        for container in players_containers:
            if '(TW)' in container.text:
                continue

            player_link = self.parser_player_id(container)
            player_id = self.db_worker.get_player_id(player_link)
            if player_id is None:
                self.db_worker.insert_new_player(container.text, player_link)
                player_id = self.db_worker.get_player_id(player_link)
            players.append(player_id)
        return players

    @staticmethod
    def parser_player_id(td):
        if a := td.find('a'):
            return a['href']

    @staticmethod
    def get_team_name(soup):
        return soup.find('h1').find_all('span')[1].text

    def get_team_id(self, team_name):
        return self.db_worker.get_team_id(team_name)

    def insert_roster_to_db(self, players, id_team):
        [self.insert_item_to_db(id_player, id_team) for id_player in players]

    def insert_item_to_db(self, id_player, id_team):
        player = {'id_team': id_team, 'id_player': id_player}
        columns = ', '.join(player.keys())
        values = [int(x) if isinstance(x, bool) else x for x in player.values()]
        self.db_worker.insert('rosters', columns, values)
