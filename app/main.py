from flask import Flask, request
from utils import utils

app = Flask(__name__)

@app.route('/init', methods=['GET'])
def init():
    args = request.args
    return utils.initForNewDay(args.get("starter"))

@app.route('/', methods=['GET'])
def nospoil():
    if utils.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {utils.tried})"
    else:
        return {
            'word': 'found ! Go to /spoil to get spoiled',
            'attempts': utils.tried
        }

@app.route('/spoil', methods=['GET'])
def spoil():
    if utils.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {utils.tried})"
    else:
        return {
            'word': Utils.today_s_word,
            'attempts': utils.tried
        }


