
# www.basketball-reference.com
class ScrapperSetting:
    TEAMS_FULL_NAME = {'atlanta hawks': 1, 'boston celtics': 2, 'brooklyn nets': 3, 'new jersey nets': 3,
                       'washington wizards': 4, 'cleveland cavaliers': 5, 'charlotte hornets': 6, 'chicago bulls': 7,
                       'dallas mavericks': 8, 'denver nuggets': 9, 'detroit pistons': 10, 'golden state warriors': 11,
                       'houston rockets': 12, 'indiana pacers': 13, 'los angeles lakers': 14,
                       'los angeles clippers': 15, 'memphis grizzlies': 16, 'vancouver grizzlies': 16, 'miami heat': 17, 'milwaukee bucks': 18,
                       'minnesota timberwolves': 19, 'new orleans pelicans': 20, 'new york knicks': 21,
                       'oklahoma city thunder': 22, 'orlando magic': 23, 'portland trail blazers': 24,
                       'philadelphia 76ers': 25, 'phoenix suns': 26, 'sacramento kings': 27, 'san antonio spurs': 28,
                       'toronto raptors': 29, 'utah jazz': 30, 'seattle supersonics': 31}

    TEAMS_SHORT_NAME = {'ATL': 1, 'BOS': 2, 'BRK': 3, 'NJN': 3, 'WAS': 4, 'CLE': 5, 'CHO': 6, 'CHH': 6, 'CHI': 7,
                        'DAL': 8, 'DEN': 9, 'DET': 10, 'GSW': 11, 'HOU': 12, 'IND': 13, 'LAL': 14, 'LAC': 15, 'MEM': 16, 'VAN': 16,
                        'MIA': 17, 'MIL': 18, 'MIN': 19, 'NOP': 20, 'NYK': 21, 'OKC': 22, 'ORL': 23, 'POR': 24,
                        'PHI': 25, 'PHO': 26, 'SAC': 27, 'SAS': 28, 'TOR': 29, 'UTA': 30, 'SEA': 31}

    TEAMS = {'atlanta hawks': 'ATL',
             'boston celtics': 'BOS',
             'brooklyn nets': 'BRK',
             'new jersey nets': 'NJN',
             'cleveland cavaliers': 'CLE',
             'charlotte hornets': ['CHO', 'CHH'],
             'chicago bulls': 'CHI',
             'dallas mavericks': 'DAL',
             'denver nuggets': 'DEN',
             'detroit pistons': 'DET',
             'golden state warriors': 'GSW',
             'houston rockets': 'HOU',
             'indiana pacers': 'IND',
             'los angeles lakers': 'LAL',
             'los angeles clippers': 'LAC',
             'memphis grizzlies': 'MEM',
             'miami heat': 'MIA',
             'milwaukee bucks': 'MIL',
             'minnesota timberwolves': 'MIN',
             'new orleans pelicans': 'NOP',
             'new york knicks': 'NYK',
             'oklahoma city thunder': 'OKC',
             'orlando magic': 'ORL',
             'portland trail blazers': 'POR',
             'philadelphia 76ers': 'PHI',
             'phoenix suns': 'PHO',
             'sacramento kings': 'SAC',
             'San Antonio Spurs': 'SAS',
             'toronto raptors': 'TOR',
             'utah jazz': 'UTA',
             'washington wizards': 'WAS'
             }

    STATS = {'player': 'starters', 'reason': 'reason', 'mp': 'minutes', 'fg': 'field_goal', 'fga': 'field_goal_attempts', 'fg3': '3p_made',
             'fg3a': '3p_attempts', 'ft': 'free_throw_made', 'fta': 'free_throw_attempts', 'orb': 'offensive_rebounds',
             'drb': 'defensive_rebounds', 'trb': 'total_rebounds',
             'ast': 'ast', 'stl': 'stl', 'blk': 'blk', 'tov': 'turnovers', 'pf': 'personal_fouls', 'pts': 'points'
             }

    ALL_STATS = {'player': 'starters', 'mp': 'mp', 'fg': 'fg', 'fga': 'fga', 'fg_pct': 'fg%', 'fg3': '3p', 'fg3a': '3pa', 'fg3_pct': '3p%', 'ft': 'ft', 'fta': 'fta', 'ft_pct': 'ft%', 'orb': 'orb', 'drb': 'drb', 'trb': 'trb', 'ast': 'ast', 'stl': 'stl', 'blk': 'blk', 'tov': 'tov', 'pf': 'pf', 'pts': 'pts', 'plus_minus': '+/-', 'ts_pct': 'ts%', 'efg_pct': 'efg%', 'fg3a_per_fga_pct': '3par', 'fta_per_fga_pct': 'ftr', 'orb_pct': 'orb%', 'drb_pct': 'drb%', 'trb_pct': 'trb%', 'ast_pct': 'ast%', 'stl_pct': 'stl%', 'blk_pct': 'blk%', 'tov_pct': 'tov%', 'usg_pct': 'usg%', 'off_rtg': 'ortg', 'def_rtg': 'drtg', 'bpm': 'bpm'}
