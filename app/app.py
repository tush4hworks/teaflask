from flask import render_template, Flask, request, url_for, redirect, flash, make_response, jsonify, abort
import logging
from flask_login import  LoginManager, login_user, login_required, logout_user, current_user
import sys
import uuid
from data import tea_list, get_timeinfo_for_all_timezones, get_timeinfo_for_all_countries
from flaskuser import User
from game_logic import game_decider, game_service
from game_logic.game import GameRound
import random
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


app = Flask(__name__)
login_manager.init_app(app)
login_manager.login_view = "login"
app.config.from_object('config.settings')

logging.basicConfig(filename = 'logs/flask.log', filemode='w', level=logging.DEBUG)

@app.route("/")
@login_required
def index():
	app.logger.debug('Plus Ultra')
	return render_template('index.html', tea='TajMahal', tea_list=tea_list, current_user=current_user)

@app.errorhandler(404)
def not_found(_):
	return make_response("This page was not found", 404)

@app.route("/tea/<tea>")
@login_required
def tea(tea):
	app.logger.debug('Gentle {}'.format(tea))
	return render_template('index.html', tea=tea, tea_list=tea_list, current_user=current_user)

@app.route("/tea/teas")
def teas():
	app.logger.debug('Serve json teas')
	return make_response(jsonify(tea_list), 200)

@app.route("/tea/timezones")
def time_by_timezones():
	return render_template('tea_by_timezones.html', timeinfo=get_timeinfo_for_all_timezones())

@app.route("/tea/countrytimes")
def time_by_country():
	return render_template('tea_by_countries.html', timeinfo=get_timeinfo_for_all_countries())

@app.route("/easter")
def wwe_attitude():
	return app.send_static_file('wwe.jpg')


@app.route("/api/game/users/<user>", methods=['GET'])
def find_user(user):
	u = game_service.find_player(user)
	if not u:
		abort(make_response(jsonify({"ERROR":"This user was not found"}), 404))
	return jsonify(u.to_json())
	
@app.route("/api/game/users", methods=['PUT'])
def put_user():
	try:
		if not(request.json) or not(request.json.get('user', None)):
			raise Exception("Provide User details")
		p = game_service.create_player(request.json.get('user'))
		return jsonify(p.to_json())
	except Exception as e:
		abort(make_response(jsonify({"Exception":str(e)}), 400))

@app.route("/api/game/games", methods=['POST'])
def create_game():
	return jsonify({"game_id":str(uuid.uuid4())})

@app.route("/api/game/rolls", methods=['GET'])
def all_rolls():
	rolls = [r.name for r in game_service.all_rolls()]
	return jsonify(rolls)

@app.route("/api/game/<gameid>/status", methods=['GET'])
def get_game_status(gameid):
	is_over = game_service.is_game_over(gameid)
	history = game_service.get_game_history(gameid)
	if not history:
		abort(make_response(jsonify({"ERROR":"This game was not found"}), 404))
	r_lookup = {r.id:r for r in game_service.all_rolls()}
	p_lookup = {p.id:p for p in game_service.all_players()}
	player_0 = game_service.find_player_by_id(history[0].player_id)
	player_1 = game_service.find_player_by_id(history[1].player_id)

	wins_p1 = game_service.count_round_wins(player_0.id, gameid)
	wins_p2 = game_service.count_round_wins(player_1.id, gameid)

	data = {'is_over': is_over,
			'player1': player_0.to_json(),
			'player2': player_1.to_json(),
			'winner': player_0.to_json() if wins_p1>=wins_p2 else player_1.to_json(),
			'moves': [h.to_json(r_lookup[h.roll_id], p_lookup[h.player_id]) for h in history]
			}

	return jsonify(data)

@app.route("/api/game/topscores", methods=['GET'])
def top_scores():
	players = game_service.all_players()
	scores = [{'player':p.to_json(), 'score':game_service.get_win_count(p)} for p in players]
	scores.sort(key=lambda x:x['score'], reverse=True)
	return jsonify(scores[:10])


@app.route('/api/game/play_round', methods=['POST'])
def play_round():
    try:
        db_roll, db_user, game_id = validate_round_request()
        computer_player = game_service.find_player('computer')
        computer_roll = random.choice(game_service.all_rolls())

        game = GameRound(game_id, db_user, computer_player, db_roll, computer_roll)
        game.play()

        return jsonify({
            'roll': db_roll.to_json(),
            'computer_roll': computer_roll.to_json(),
            'player': db_user.to_json(),
            'opponent': computer_player.to_json(),
            'round_outcome': str(game.decision_p1_to_p2),
            'is_final_round': game.is_over,
            'round_number': game.round
        })
    except Exception as x:
        # raise x
        abort(make_response(jsonify({'Invalid request': '{}'.format(x)}), 400))

def validate_round_request():
    if not request.json:
        raise Exception("Invalid request: no JSON body.")
    game_id = request.json.get('game_id')
    if not game_id:
        raise Exception("Invalid request: No game_id value")
    user = request.json.get('user')
    if not user:
        raise Exception("Invalid request: No user value")
    db_user = game_service.find_player(user)
    if not db_user:
        raise Exception("Invalid request: No user with name {}".format(user))
    roll = request.json.get('roll')
    if not roll:
        raise Exception("Invalid request: No roll value")
    db_roll = game_service.find_roll(roll)
    if not db_roll:
        raise Exception("Invalid request: No roll with name {}".format(roll))

    is_over = game_service.is_game_over(game_id)
    if is_over:
        raise Exception("This game is already over.")

    return db_roll, db_user, game_id

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		user = User(request.form['userid'])
		#do some validation
		login_user(user)
		flash('Logged in successfully.')
		next = request.args.get('next')
		# is_safe_url should check if the url is safe for redirects.
		# See http://flask.pocoo.org/snippets/62/ for an example.
		'''
		if not is_safe_url(next):
		    return flask.abort(400)
		Shall implement this later -> https://web.archive.org/web/20190128010142/http://flask.pocoo.org/snippets/62/
		'''
		return redirect(next or url_for('index'))
	return '''
	    <form method="post">
	        <p><input type=text name=userid>
	        <p><input type=submit value=Login>
	    </form>
	    '''

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

def build_starter_data():
	rolls = game_decider.all_roll_names()
	game_service.init_rolls(rolls)
	if not game_service.find_player('computer'):
		game_service.create_player('computer')

if __name__ == '__main__':
	build_starter_data()
	app.run(host='0.0.0.0', debug=True)

