from flask import Flask, request
from utils import utils

app = Flask(__name__)


@app.route('/init', methods=['GET'])
def init():
    args = request.args
    return utils.get_today_s_word(args.get("starter"))


@app.route('/', methods=['GET'])
def no_spoil():
    row = utils.get_todays_row()
    return {
        'word': "go to /spoil to get spoiled",
        'index_history': row[2],
        'time_to_resolution': f"{row[3]} s",
        'word_history': "go to /spoil to get spoiled",
        'guess_history': row[6],
    }


@app.route('/spoil', methods=['GET'])
def spoil():
    row = utils.get_todays_row()
    return {
        'word': row[1],
        'index_history': row[2],
        'time_to_resolution': f"{row[3]} s",
        'word_history': row[5],
        'guess_history': row[6],
    }


@app.route('/history', methods=['GET'])
def history():
    rows = utils.get_all_rows()
    return {
        'history': [
            {
                'word': row[1],
                'index_history': row[2],
                'time_to_resolution': f"{row[3]} s",
                'word_history': row[5],
                'guess_history': row[6],
            } for row in rows
        ]
    }
