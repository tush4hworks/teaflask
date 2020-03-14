import uplink
from uplink import Consumer, Body, get, put, post, returns, response_handler, json
import random
from collections import defaultdict
from pprint import pprint

def raise_for_status(response):
    """Checks whether or not the response was successful."""
    if 200 <= response.status_code < 300:
        # Pass through the response.
        return response

    print('Request resulted in error')
    return response

@response_handler(raise_for_status)
class teaflaskclinet(Consumer):

	@returns.json
	@get("api/game/rolls")
	def get_rolls(self):
		"""get rolls"""
	

	@returns.json
	@get("api/game/users/{user}")
	def get_user(self, user):
		"""return use"""

	@json
	@returns.json
	@put("api/game/users")
	def create_user(self, userinfo: Body):
		""" post body """    

	@returns.json
	@post("api/game/games")
	def create_game(self):
		""" create new game """

	@returns.json
	@get("api/game/{gameid}/status")
	def get_game_status(self, gameid):
		""" get game status """

	@returns.json
	@get("api/game/topscores")
	def get_topscores(self):
		""" get topscores """

	@json
	@returns.json
	@post("api/game/play_round")
	def playround(self, roundinfo: Body):
		""" play a round """


def playGame():
	t = teaflaskclinet(base_url='http://localhost:5000/')
	rolls = (t.get_rolls())
	print(t.get_user('tony'))
	print(t.create_user({'user':'tony'}))
	game_id = (t.create_game()).get('game_id')
	print(game_id)
	while not(t.get_game_status(game_id).get('is_over')):
		roll = input('\n What do you want to throw among {} ?\n'.format(rolls))
		if roll not in rolls:
			print("Choose one of the above")
			continue
		rnd = (t.playround({"user":"tony","game_id":game_id,"roll": roll}))
		print("You threw a {}".format(roll))
		print("Computer threw a {}".format(rnd.get('computer_roll').get('name')))
		print("You {} this round".format(rnd.get('round_outcome')))
	print("Game Over")
	gamestatus = t.get_game_status(game_id)
	print('Winner is {}'.format(gamestatus.get('winner').get('name')))
	print(t.get_topscores())

if __name__ == '__main__':
	playGame()
	