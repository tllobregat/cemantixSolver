from gensim.models import KeyedVectors
import requests
from time import sleep

class Utils:
    model_url = "https://embeddings.net/embeddings/frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin"
    loading = False
    today_s_word = ''
    tried = 0


    def reset():
        Utils.loading = True
        Utils.today_s_word = ''
        Utils.tried = 0


    def guess(word):
        Utils.tried += 1
        return requests.post('https://cemantix.herokuapp.com/score', data = {'word': word}).json()['score']


    def may_word_be_closed(score_1, score_2, difference):
        return abs(score_1 - score_2) < difference

    def findTodaysWord(model):
        random_tried_1 = 'truc'
        random_tried_2 = 'ville'

        score_1 = Utils.guess(random_tried_1)
        sleep(2)
        score_2 = Utils.guess(random_tried_2)

        word_to_try = []

        difference_to_test = 0.0001
        while len(word_to_try) == 0:
            print("Testing with difference ", difference_to_test)

            for word in model.index_to_key :
                similarity = model.similarity(word, score_1)
                similarity_2 = model.similarity(word, score_2)

                if Utils.may_word_be_closed(similarity, score_1, difference_to_test) and Utils.may_word_be_closed(similarity_2, score_2, difference_to_test):
                    print(f"Word may be {word}")
                    word_to_try.append(word)
                    break
            difference_to_test *= 2
        
        return word_to_try



    def initForNewDay():
        print("Initializing for new day")
        Utils.reset()

        print("Loading model")
        model = KeyedVectors.load_word2vec_format(Utils.model_url, binary=True, unicode_errors="ignore")
        print("Loading complete")

        Utils.today_s_word = Utils.findTodaysWord(model)
        Utils.loading = False
