import pandas as pd
from datetime import datetime
from .setting import ScrapperSetting
from .tools import BSTools


class RosterScrapper:

    def __init__(self):
        self.bs_tools = BSTools()

    def update(self):
        links = self.get_links()
        self.process_teams(links)

    def get_links(self):
        soup = self.bs_tools.get_soup('https://www.basketball-reference.com/teams/')
        a = soup.find('div', id='all_teams_active').find_all('a')
        return ['https://www.basketball-reference.com/teams/' + ScrapperSetting.TEAMS[item.text.lower()] + '/' + str(datetime.now().year) + '.html' for item in a]

    def process_teams(self, links):
        for link in links:
            self.process_team(link)

    def process_team(self, link):
        soup = self.bs_tools.get_soup(link)
        players_containers = soup.find('div', id='div_roster').find_all("td", {"data-stat": "player"})
        players = self.get_players(players_containers)
        self.update_roster(players, link.split('/')[-2])

    def get_players(self, players_containers):
        names = []
        for container in players_containers:
            if '(TW)' in container.text:
                continue
            player_id = self.parser_player_id(container)
            name = player_id + '_' + container.text.replace(' ', '_')
            names.append(name)
        return names

    @staticmethod
    def parser_player_id(td):
        if a := td.find('a'):
            return a['href'].split('/')[-1].replace('.html', '')

    @staticmethod
    def update_roster(players, team):
        df = pd.DataFrame(players, columns=["players"])
        df.to_csv('data/roster/' + team + '.csv', index=False)
