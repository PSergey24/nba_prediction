from .tools import BSTools


class PlayerScrapper:

    def __init__(self, player_id):
        self.player_id = player_id
        self.bs_tools = BSTools()

    def get_position(self):
        soup = self.bs_tools.get_soup('https://www.basketball-reference.com/players/'
                                      + self.player_id[0] + '/' + self.player_id + '.html')
