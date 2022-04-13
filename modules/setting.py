
# www.basketball-reference.com
class ScrapperSetting:
    TEAMS = {'brooklyn nets': 'BRK',
             'charlotte hornets': 'CHO',
             'chicago bulls': 'CHI',
             'detroit pistons': 'DET',
             'houston rockets': 'HOU',
             'indiana pacers': 'IND',
             'los angeles lakers': 'LAL',
             'los angeles clippers': 'LAC',
             'miami heat': 'MIA',
             'new orleans pelicans': 'NOP',
             'philadelphia 76ers': 'PHI',
             'toronto raptors': 'TOR'
             }
    STATS = {'player': 'starters', 'reason': 'reason', 'mp': 'minutes', 'fg': 'field_goal', 'fga': 'field_goal_attempts', 'fg3': '3p_made',
             'fg3a': '3p_attempts', 'ft': 'free_throw_made', 'fta': 'free_throw_attempts', 'orb': 'offensive_rebounds',
             'drb': 'defensive_rebounds', 'trb': 'total_rebounds',
             'ast': 'ast', 'stl': 'stl', 'blk': 'blk', 'tov': 'turnovers', 'pf': 'personal_fouls', 'pts': 'points'
             }

    ALL_STATS = {'player': 'starters', 'mp': 'mp', 'fg': 'fg', 'fga': 'fga', 'fg_pct': 'fg%', 'fg3': '3p', 'fg3a': '3pa', 'fg3_pct': '3p%', 'ft': 'ft', 'fta': 'fta', 'ft_pct': 'ft%', 'orb': 'orb', 'drb': 'drb', 'trb': 'trb', 'ast': 'ast', 'stl': 'stl', 'blk': 'blk', 'tov': 'tov', 'pf': 'pf', 'pts': 'pts', 'plus_minus': '+/-', 'ts_pct': 'ts%', 'efg_pct': 'efg%', 'fg3a_per_fga_pct': '3par', 'fta_per_fga_pct': 'ftr', 'orb_pct': 'orb%', 'drb_pct': 'drb%', 'trb_pct': 'trb%', 'ast_pct': 'ast%', 'stl_pct': 'stl%', 'blk_pct': 'blk%', 'tov_pct': 'tov%', 'usg_pct': 'usg%', 'off_rtg': 'ortg', 'def_rtg': 'drtg', 'bpm': 'bpm'}
