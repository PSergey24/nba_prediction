from __future__ import annotations
import csv
import os.path
from bs4 import BeautifulSoup
from typing import List
from .setting import ScrapperSetting
from .elo_counter import EloCounter
from .tools import BSTools
from .state_worker import StateWorker, State


class GameScrapper:

    def __init__(self, link: str, season: str, state: State):
        self.setting = ScrapperSetting()
        self.state_worker = StateWorker()
        self.bs_tools = BSTools()
        self.elo_counter = EloCounter()

        self.link = link
        self.season = season
        self.state = state

        self.season_stage = None
        self.time = None
        self.arena = None
        self.visitor = None
        self.home = None
        self.score = None

    def main(self):
        soup = self.bs_tools.get_soup(self.link)
        self.parse_data(soup)
        self.get_game_rosters()
        self.update_elo_rating()
        self.save_data_to_csv()
        print(f'Game {self.visitor.name} - {self.home.name} was parsed. Season {self.season}, {self.time}')

    def parse_data(self, soup: BeautifulSoup) -> None:
        self.parse_info_about_game(soup)
        self.parse_game_table(soup)

    def parse_info_about_game(self, soup: BeautifulSoup) -> None:
        self.parse_h(soup)
        self.parse_date(soup)
        self.parse_teams(soup)
        self.parse_inactive(soup)

    def parse_h(self, soup: BeautifulSoup) -> None:
        h1 = soup.find('h1')
        stage = h1.text.split(':')
        if len(stage) == 1:
            self.season_stage = 'Regular Season'
        elif stage[0] == 'Play-In Game':
            self.season_stage = 'Play-In Game'
        else:
            self.season_stage = " ".join(stage[0].split(' ')[-4:-2])

    def parse_date(self, soup: BeautifulSoup) -> None:
        score_meta = soup.find('div', class_='scorebox_meta')
        score_box_rows = score_meta.find_all('div')
        self.time = score_box_rows[0].text
        self.arena = score_box_rows[1].text

    def parse_teams(self, soup: BeautifulSoup) -> None:
        score_boxes = soup.find_all('div', class_='scores')

        teams = []
        for i, box in enumerate(score_boxes):
            a = box.parent.find("a", {"itemprop": "name"})
            short_name = a.attrs['href'].split('/')[-2]
            is_home = False if i == 0 else True

            teams.append(Team(short_name, box.nextSibling.text, is_home, box.text.replace('\n', '')))

        self.visitor, self.home = teams[0], teams[1]
        self.visitor.opponent, self.home.opponent = self.home.name, self.visitor.name
        self.score = str(self.visitor.score) + '-' + str(self.home.score)

    def parse_inactive(self, soup: BeautifulSoup) -> None:
        wrap = soup.find('div', id='all_box-' + self.home.name + '-game-advanced', class_="section_wrapper")
        inactive_box = wrap.nextSibling.nextSibling
        if inactive_box is not None:
            pos = inactive_box.text.find('Officials')
            text = inactive_box.text[:pos].split(self.home.name)
            if len(text) > 1:
                inactive_links = inactive_box.find('div').find_all('a')
                for a in inactive_links:
                    link = a.attrs['href'].split('/')[-1].replace('.html', '')
                    name = a.text.replace(' ', '_')
                    if a.text in text[0]:
                        self.visitor.inactive.append(link + '_' + name)
                    elif a.text in text[1]:
                        self.home.inactive.append(link + '_' + name)

    def parse_game_table(self, soup: BeautifulSoup) -> None:
        for team_object in [self.visitor, self.home]:
            team_object.players = self.parse_players_info(soup, team_object.name)
            team_object.stats = self.parse_team_info(soup, team_object.name)

    def parse_players_info(self, soup: BeautifulSoup, team_name: str) -> dict:
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

    def parse_row(self, fields: dict, td_list: List) -> dict:
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

            if stat_name == 'starters':
                if link := self.parser_player_id(td):
                    new_name = link + '_' + td_list[0].text.replace(' ', '_')
                    fields[new_name] = fields.pop(td_list[0].text)
                    td_list[0].string = new_name
        return fields

    @staticmethod
    def get_stats(fields: dict, td_list: List) -> dict:
        if 'reason' not in fields[td_list[0].text]:
            if fields[td_list[0].text]['field_goal_attempts'] != '' and fields[td_list[0].text]['field_goal'] != '':
                field_goal_miss = int(
                    int(fields[td_list[0].text]['field_goal_attempts']) - int(fields[td_list[0].text]['field_goal']))
            else:
                field_goal_miss = ''
            fields[td_list[0].text].update({'field_goal_miss': field_goal_miss})

            if fields[td_list[0].text]['free_throw_attempts'] != '' and fields[td_list[0].text]['free_throw_made'] != '':
                free_throw_miss = int(
                    int(fields[td_list[0].text]['free_throw_attempts']) - int(fields[td_list[0].text]['free_throw_made']))
            else:
                free_throw_miss = ''
            fields[td_list[0].text].update({'free_throw_miss': free_throw_miss})
        return fields

    @staticmethod
    def stat_preprocessing(stat_name: str, value: str):
        if stat_name not in ['starters', 'minutes', 'reason']:
            value = int(value) if value != '' else value
        return value

    @staticmethod
    def parser_player_id(td):
        if a := td.find('a'):
            return a['href'].split('/')[-1].replace('.html', '')

    def players_postprocessing(self, players: dict) -> dict:
        players = self.get_per(players)
        return players


    # Player Efficiency Ratings
    # PER = (FGM x 85.910 + Steals x 53.897 + 3PTM x 51.757 + FTM x 46.845
    # + Blocks x 39.190 + Offensive_Reb x 39.190 + Assists x 34.677 +
    # Defensive_Reb x 14.707 — Foul x 17.174 — FT_Miss x 20.091 — FG_Miss x 39.190 — TO x 53.897) x (1 / Minutes)
    @staticmethod
    def get_per(fields: dict) -> dict:
        for i, (key, value) in enumerate(fields.items()):
            # Did Not Play or other... row w/o stats
            if 'reason' in fields[key]:
                continue

            time = value['minutes'].split(':')
            m = time[0]
            s = time[1] if len(time) > 1 else 0
            value_time = round((int(m) * 60 + int(s)) / 60, 3)

            PER = value['field_goal'] * 85.910 + value['stl'] * 53.897 + value['3p_made'] * 51.757 + \
                  value['free_throw_made'] * 46.845 + value['blk'] * 39.190 + value['offensive_rebounds'] * 39.190 + \
                  value['ast'] * 34.677 + value['defensive_rebounds'] * 14.707 - value['personal_fouls'] * 17.174 - \
                  value['free_throw_miss'] * 20.091 - value['field_goal_miss'] * 39.190 - value['turnovers'] * 53.897

            if value_time == 0:
                PER = 0
            else:
                PER *= (1 / value_time)

            fields[key].update({'PER': round(PER, 3)})
        return fields

    def parse_team_info(self, soup: BeautifulSoup, team_name: str) -> dict:
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

    def team_postprocessing(self, team: dict, quarter: str) -> dict:
        team = self.remove_stats(team)
        team = self.rename_stats(team, quarter)
        return team

    @staticmethod
    def remove_stats(team: dict) -> dict:
        team.pop('minutes')
        return team

    @staticmethod
    def rename_stats(team: dict, quarter: str) -> dict:
        if quarter != 'game':
            new_team = {}
            for key, value in team.items():
                new_team.update({quarter + '_' + key: team[key]})
            return new_team
        return team

    def get_game_rosters(self):
        self.home.roster = self.get_roster(self.home.players)
        self.visitor.roster = self.get_roster(self.visitor.players)

    @staticmethod
    def get_roster(players_dict: dict) -> List[str]:
        return [key for key in players_dict if 'reason' not in players_dict[key]]

    def update_elo_rating(self) -> None:
        visitor_old, home_old = self.get_old_elo_rating(self.state.teams_elo_rating)
        self.visitor.elo_rating = self.elo_counter.get_elo(visitor_old, home_old, int(self.visitor.score), int(self.home.score))
        self.home.elo_rating = self.elo_counter.get_elo(home_old, visitor_old, int(self.home.score), int(self.visitor.score))
        self.save_new_elo()

    def get_old_elo_rating(self, elo_state: dict):
        if elo_state:
            visitor_elo = self.get_item_elo_rating(elo_state, self.setting.TEAMS_SHORT_NAME[self.visitor.name])
            home_elo = self.get_item_elo_rating(elo_state, self.setting.TEAMS_SHORT_NAME[self.home.name])
        else:
            visitor_elo, home_elo = 1500, 1500
        return visitor_elo, home_elo

    @staticmethod
    def get_item_elo_rating(elo_state, id_team):
        return elo_state[id_team] if id_team in elo_state else 1500

    def save_new_elo(self) -> None:
        self.state.teams_elo_rating.update({self.setting.TEAMS_SHORT_NAME[self.visitor.name]: self.visitor.elo_rating})
        self.state.teams_elo_rating.update({self.setting.TEAMS_SHORT_NAME[self.home.name]: self.home.elo_rating})
        self.state_worker.save_state(self.state)

    def save_data_to_csv(self) -> None:
        self.save_teams_stats()
        self.save_players_stats()

    def save_teams_stats(self) -> None:
        self.save_team(self.visitor)
        self.save_team(self.home)

    def save_team(self, team: Team) -> None:
        name = 'data/row_data/teams/' + team.name + '_games.csv'
        is_exist = os.path.exists(name)
        data = [str(item) for item in team.stats.values()]
        data = [self.season, self.season_stage, self.link, team.record, str(team.is_home), team.opponent, self.score,
                ", ".join(team.roster), ", ".join(team.inactive), team.elo_rating, self.time] + data

        with open(name, 'a') as csvfile:
            writer = csv.writer(csvfile)
            if is_exist is False:
                header = list(team.stats.keys())
                header = ['season', 'season_stage', 'link', 'record', 'is_home', 'opponent', 'score', 'roster',
                          'inactive', 'ELO', 'time'] + header
                writer.writerow(header)
            writer.writerow(data)

    def save_players_stats(self) -> None:
        self.save_players(self.visitor)
        self.save_players(self.home)

    def save_players(self, team: Team) -> None:
        for player in team.players:
            # player not played
            if 'reason' in team.players[player]:
                continue

            name = 'data/row_data/players/' + player + '.csv'
            is_exist = os.path.exists(name)
            data = [str(item) for item in team.players[player].values()]
            data = [self.season, team.name, self.score, team.opponent, str(team.is_home), self.time] + data

            with open(name, 'a') as csvfile:
                writer = csv.writer(csvfile)
                if is_exist is False:
                    header = list(team.players[player].keys())
                    header = ['season', 'team', 'score', 'opponent', 'is_home', 'time'] + header
                    writer.writerow(header)
                writer.writerow(data)


class Team:

    def __init__(self, name, record, is_home, score):
        self.name = name
        self.record = record
        self.is_home = is_home
        self.opponent = None
        self.score = score
        self.players = None
        self.stats = None
        self.elo_rating = None
        self.roster = None
        self.inactive = []
