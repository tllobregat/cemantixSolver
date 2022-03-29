from multiprocessing.connection import wait
import re
from flask import Flask
from gensim.models import KeyedVectors
import requests
from time import sleep

app = Flask(__name__)

class Utils:
    model_url = "https://embeddings.net/embeddings/frWac_non_lem_no_postag_no_phrase_200_skip_cut100.bin"
    loading = False
    today_s_word = ''
    tried = 0


    def reset():
        Utils.loading = True
        Utils.today_s_word = ''
        Utils.tried = 0


    def guess(word):
        if not word.endswith('es') and not word.endswith('ée'):
            Utils.tried += 1
            req = requests.post('https://cemantix.herokuapp.com/score', data = {'word': word}).json()
            sleep(1.5)

            if 'score' in req:
                return req['score']
        
        return -1000


    def may_word_be_closed(score_1, score_2, difference):
        return abs(abs(score_1) - abs(score_2)) < difference


    def mapToList(mapContainer):
        return map(lambda l: l['word'], mapContainer)


    def findTodaysWord(model):
        starter = 'ville'
        starter_guess = Utils.guess(starter)
        word_tried = [{'word': starter, 'guess': starter_guess}]
        word_denied = []
        word_found = ''

        difference_to_test = 0.0001
        while word_found == '':
            print(f"Testing with difference {difference_to_test} for words {word_tried}")

            for word in model.index_to_key :
                if word not in Utils.mapToList(word_tried) and word not in word_denied:
                    word_worth_try = True

                    for index in range(len(word_tried)):
                        similarity = model.similarity(word, word_tried[index]['word'])

                        if not Utils.may_word_be_closed(similarity, word_tried[index]['guess'], difference_to_test):
                            word_worth_try = False
                            break

                    if word_worth_try:
                        guess = Utils.guess(word)
                        if guess != -1000:
                            word_tried.append({'word': word, 'guess': guess})
                            print(f"Word may be {word} : {guess}")

                            if guess > 0.99:
                                word_found = word
                                break

                            if len(list(filter(lambda l: l['guess'] > 0.2, word_tried))) > 0:
                                word_tried = list(filter(lambda l: l['guess'] > 0.2, word_tried))
                                break
                        else:
                            word_denied.append(word)

            difference_to_test *= 2

        return word_found


    def initForNewDay():
        print("Initializing for new day")
        Utils.reset()

        print("Loading model")
        model = KeyedVectors.load_word2vec_format(Utils.model_url, binary=True, unicode_errors="ignore")
        print("Loading complete")

        Utils.today_s_word = Utils.findTodaysWord(model)
        Utils.loading = False
        return Utils.today_s_word

@app.route('/init', methods=['GET'])
def init():
    return Utils.initForNewDay()

@app.route('/', methods=['GET'])
def nospoil():
    if Utils.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {Utils.tried}"
    else:
        return {
            'word': 'found ! Go to /spoil to get spoiled',
            'attempts': Utils.tried
        }

@app.route('/spoil', methods=['GET'])
def spoil():
    if Utils.today_s_word == '':
        return f"App is loading, please wait a sec. (Current attempts : {Utils.tried}"
    else:
        return {
            'word': Utils.today_s_word,
            'attempts': Utils.tried
        }


