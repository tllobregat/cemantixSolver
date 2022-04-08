from flask import Flask, request
from utils import utils
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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


@app.route('/front-data', methods=['GET'])
def front_data():
    row = utils.get_todays_row()
    index_history = row[2][1:-1].split(", ")
    word_history = row[5][1:-1].split(", ")[:-1]
    guess_history = row[6][1:-1].split(", ")[:-1]

    if len(index_history) != len(word_history) or len(word_history) != len(guess_history):
        raise Exception("Internal Error")

    return {
        'today_s_date': row[0],
        'today_s_word': row[1],
        'time_to_found': row[3],
        'word_history': [
            {
                "index": index_history[i],
                "word": word_history[i].replace("'", ""),
                "guess": guess_history[i]
            } for i in range(len(index_history))
        ]
    }
