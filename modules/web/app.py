import os
import sys
sys.path.append(os.getcwd())

from modules.db_worker import DBWorker
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    db_worker = DBWorker('data/db/nba.db')
    data = db_worker.get_active_franchises()
    return render_template('index.html', teams=data)


@app.route('/team<int:team_id>')
def post(team_id):
    db_worker = DBWorker('data/db/nba.db')
    data = db_worker.get_games_by_team(team_id)
    return render_template('team.html', games=data)
