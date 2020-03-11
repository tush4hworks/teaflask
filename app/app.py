from flask import render_template, Flask, request, url_for, redirect, flash
import logging
from flask_login import  LoginManager, login_user, login_required, logout_user, current_user
import sys
from data import tea_list, get_timeinfo_for_all_timezones, get_timeinfo_for_all_countries
from flaskuser import User
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

@app.route("/tea/<tea>")
@login_required
def tea(tea):
	app.logger.debug('Gentle {}'.format(tea))
	return render_template('index.html', tea=tea, tea_list=tea_list, current_user=current_user)

@app.route("/tea/timezones")
def time_by_timezones():
	return render_template('tea_by_timezones.html', timeinfo=get_timeinfo_for_all_timezones())

@app.route("/tea/countrytimes")
def time_by_country():
	return render_template('tea_by_countries.html', timeinfo=get_timeinfo_for_all_countries())

@app.route("/easter")
def wwe_attitude():
	return app.send_static_file('wwe.jpg')

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
		return redirect(next or flask.url_for('index'))
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

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
