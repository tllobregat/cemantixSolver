from gensim.models import KeyedVectors
import requests
from vars import vars


def reset():
    vars.today_s_word = ''
    vars.tried = 0


def guessWord(word):
    vars.tried += 1
    req = requests.post('https://cemantix.herokuapp.com/score', data = {'word': word}).json()
    if 'score' in req:
        return req['score']
            
    return -1000


def computeEcart(score_1, score_2):
    return abs(score_1 - score_2)


def mapToList(mapContainer):
    return map(lambda l: l['word'], mapContainer)


def isWordWorthToTry(word_tried, model, word, difference_to_test):
    word_worth_try = True
    total_similarity = 0

    for index in range(len(word_tried)):
        similarity = model.similarity(word, word_tried[index]['word'])
        ecart = computeEcart(similarity, word_tried[index]['guess'])
        total_similarity += ecart

        if ecart > difference_to_test:
            word_worth_try = False
            break

    return word_worth_try, total_similarity


def findTodaysWord(starter, model):
    starter_guess = guessWord(starter)
    word_tried = [{'word': starter, 'guess': starter_guess}]
    word_denied = []
    word_found = ''

    difference_to_test = 0.005
    while word_found == '':
        words_worth_to_try = []
        print(f"Testing with difference {difference_to_test} for words {word_tried}")

        for word in model.index_to_key :
            if word not in mapToList(word_tried) and word not in word_denied and not word.endswith('es') and not word.endswith('ée') and not word.endswith('eaux'):
                word_worth_to_try, total_similarity = isWordWorthToTry(word_tried, model, word, difference_to_test)
                if word_worth_to_try:
                    words_worth_to_try.append({'word': word, 'total': total_similarity})

        if len(words_worth_to_try) > 0:
            word = sorted(words_worth_to_try, key=lambda w: w['total'])[0]['word']

            guess = guessWord(word)
            if guess != -1000:
                word_tried.append({'word': word, 'guess': guess})
                print(f"Word may be {word} : {guess}")

                if guess > 0.99:
                    word_found = word
                    break

                if guess > 0.2:
                    if len(list(filter(lambda l: l['guess'] > 0.2, word_tried))) > 0:
                        word_tried = list(filter(lambda l: l['guess'] > 0.2, word_tried))
                                    
                    difference_to_test = 0.001
            else:
                word_denied.append(word)
                        

        difference_to_test *= 2

    print(word_denied)

    return word_found


def initForNewDay(starter):
    print("Initializing for new day")
    reset()

    print("Loading model")
    model = KeyedVectors.load_word2vec_format(vars.model_url, binary=True, unicode_errors="ignore")

    vars.today_s_word = findTodaysWord(starter, model)
    return vars.today_s_word
