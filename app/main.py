from flask import Flask, request
from utils import utils
from vars import vars

app = Flask(__name__)

@app.route('/init', methods=['GET'])
def init():
    args = request.args
    return utils.initForNewDay(args.get("starter"))

@app.route('/', methods=['GET'])
def nospoil():
    if vars.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {vars.tried})"
    else:
        return {
            'word': 'found ! Go to /spoil to get spoiled',
            'attempts': utils.tried
        }

@app.route('/spoil', methods=['GET'])
def spoil():
    if vars.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {vars.tried})"
    else:
        return {
            'word': vars.today_s_word,
            'attempts': vars.tried
        }


