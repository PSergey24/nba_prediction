import requests
import pandas as pd
from .setting import ScrapperSetting
from bs4 import BeautifulSoup


class TableField:
    def __init__(self, name):
        self.name = name
        self.stats = {}


class DataScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()
        self.game_scrapper = GameScrapper()

    def main(self):
        url = 'https://www.basketball-reference.com/boxscores/202008140HOU.html'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.game_scrapper.parse_data(soup)

        # soup.find_all('div', class_='body')


class GameScrapper:

    def __init__(self):
        self.setting = ScrapperSetting()

    def parser_game_page(self):
        pass

    def parse_data(self, soup):
        time, arena = self.parse_info_about_game(soup)
        P, T = self.parse_game_table(soup)
        print(1)

    def parse_info_about_game(self, soup):
        score_box = soup.find('div', class_='scorebox_meta')
        score_box_rows = score_box.find_all('div')
        time = score_box_rows[0].text
        arena = score_box_rows[1].text
        return time, arena

    def parse_game_table(self, soup):
        # away, home
        P, T = [], []
        for team_name in ['PHI', 'HOU']:
            players = self.parse_players_info(soup, team_name)
            team = self.parse_team_info(soup, team_name)
            P.append(players)
            T.append(team)
        return P, T

    def parse_team_info(self, soup, team_name):
        result = {}
        for quarter in ['game', 'q1', 'q2', 'q3', 'q4']:
            table_id = 'box-' + team_name + '-' + quarter + '-basic'

            fields = {}
            table = soup.find(id=table_id)
            tr_list = [table.find_all('tr')[-1]]
            for i, tr in enumerate(tr_list):
                td_list = tr.find_all(['th', 'td'])
                fields = self.parse_row(fields, td_list)
                fields = self.get_stats(fields, td_list)

            team = fields.pop('Team Totals')
            team = self.team_postprocessing(team, quarter)
            result.update(team)
        return result

    def team_postprocessing(self, team, quarter):
        team = self.remove_stats(team)
        team = self.rename_stats(team, quarter)
        return team

    @staticmethod
    def remove_stats(team):
        team.pop('minutes')
        return team

    @staticmethod
    def rename_stats(team, quarter):
        if quarter != 'game':
            new_team = {}
            for key, value in team.items():
                new_team.update({quarter + '_' + key: team[key]})
            return new_team
        return team

    def parse_players_info(self, soup, team_name):
        table_id = 'box-' + team_name + '-game-basic'

        fields = {}
        table = soup.find(id=table_id)
        tr_list = table.find_all('tr')

        for i, tr in enumerate(tr_list):
            # reserves_row_head
            if i in [0, 1, 7, len(tr_list) - 1]:
                continue

            td_list = tr.find_all(['th', 'td'])
            fields = self.parse_row(fields, td_list)
            fields = self.get_stats(fields, td_list)

        players = self.players_postprocessing(fields)
        return players

    def parse_row(self, fields, td_list):
        for j, td in enumerate(td_list):
            if td['data-stat'] not in self.setting.STATS:
                continue

            stat_name = self.setting.STATS[td['data-stat']]
            value = td.text
            value = self.stat_preprocessing(stat_name, value)

            if j == 0:
                fields.update({value: {}})
            else:
                fields[td_list[0].text].update({stat_name: value})
        return fields

    @staticmethod
    def get_stats(fields, td_list):
        if len(fields[td_list[0].text]) > 0:
            field_goal_miss = int(
                int(fields[td_list[0].text]['field_goal_attempts']) - int(fields[td_list[0].text]['field_goal']))
            fields[td_list[0].text].update({'field_goal_miss': field_goal_miss})

            free_throw_miss = int(
                int(fields[td_list[0].text]['free_throw_attempts']) - int(fields[td_list[0].text]['free_throw_made']))
            fields[td_list[0].text].update({'free_throw_miss': free_throw_miss})
        return fields

    @staticmethod
    def stat_preprocessing(stat_name, value):
        if stat_name not in ['starters', 'minutes']:
            value = int(value)
        return value

    def players_postprocessing(self, players):
        players = self.get_per(players)
        return players


    # Player Efficiency Ratings
    # PER = (FGM x 85.910 + Steals x 53.897 + 3PTM x 51.757 + FTM x 46.845
    # + Blocks x 39.190 + Offensive_Reb x 39.190 + Assists x 34.677 +
    # Defensive_Reb x 14.707 — Foul x 17.174 — FT_Miss x 20.091 — FG_Miss x 39.190 — TO x 53.897) x (1 / Minutes)
    @staticmethod
    def get_per(fields):
        for i, (key, value) in enumerate(fields.items()):
            if len(fields[key]) == 0:
                continue

            time = value['minutes'].split(':')
            m = time[0]
            s = time[1] if len(time) > 1 else 0
            value_time = round((int(m) * 60 + int(s)) / 60, 3)

            PER = value['field_goal'] * 85.910 + value['stl'] * 53.897 + value['3p_made'] * 51.757 + \
                  value['free_throw_made'] * 46.845 + value['blk'] * 39.190 + value['offensive_rebounds'] * 39.190 + \
                  value['ast'] * 34.677 + value['defensive_rebounds'] * 14.707 - value['personal_fouls'] * 17.174 - \
                  value['free_throw_miss'] * 20.091 - value['field_goal_miss'] * 39.190 - value['turnovers'] * 53.897
            PER *= (1 / value_time)

            fields[key].update({'PER': round(PER, 3)})
        return fields

    # get list of stats/columns
    @staticmethod
    def get_table_fields():
        url = 'https://www.basketball-reference.com/boxscores/202008140HOU.html'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        table_list = ['box-PHI-game-basic', 'box-PHI-game-advanced']
        stats = {}
        for item in table_list:
            table = soup.find(id=item)
            starters = table.find(text="Starters")
            starters_parent = starters.parent.parent
            th_list = starters_parent.find_all('th')

            for th in th_list:
                data_stat = th['data-stat']
                text = th.text
                stats.update({data_stat.lower(): text.lower()})
        print(stats)
