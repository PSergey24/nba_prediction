class NormalizerSetting:
    stats_drop_lists = {'teams': ['Unnamed: 0', 'season', 'season_stage', 'link', 'record', 'is_home', 'opponent', 'score', 'roster',
                                  'inactive', 'time'],
                        'teams_10_average': ['Unnamed: 0', 'season', 'time'],
                        'players': ['season', 'team', 'score', 'opponent', 'is_home', 'time', 'minutes'],
                        'players_10_average': ['Unnamed: 0', 'season', 'time'],
                        'players_season_average': ['Unnamed: 0', 'season']}

    stats_directories = {'teams': 'data/clean_data/teams/cleaned/',
                         'teams_10_average': 'data/clean_data/teams/10_games_average/',
                         'players': 'data/raw_data/players/',
                         'players_10_average': 'data/clean_data/players/10_games_average/',
                         'players_season_average': 'data/clean_data/players/seasons_average/'}
