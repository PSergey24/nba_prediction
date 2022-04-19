import math


class EloCounter:

    @staticmethod
    def get_elo(team_elo, opp_elo, team_score, opp_score):
        mov = abs(team_score - opp_score)
        if team_score > opp_score:
            elo_difference_winner = team_elo - opp_elo
            s_team = 1
        else:
            elo_difference_winner = opp_elo - team_elo
            s_team = 0

        e_team = 1 / (1 + math.pow(10, (opp_elo - team_elo)/400))
        k = 20 * (math.pow(mov + 3, 0.8))/(7.5 + 0.006 * elo_difference_winner)

        new_rating = k * (s_team - e_team) + team_elo
        return new_rating
