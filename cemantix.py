from time import sleep
from gensim.models import KeyedVectors
import requests
import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True

print("Loading word")
model = KeyedVectors.load_word2vec_format("frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin", binary=True, unicode_errors="ignore")
print("Loading complete")

random_tried = 'truc'
random_tried_2 = 'ville'

@app.route('/', methods=['GET'])
def home():
    r = requests.post('https://cemantix.herokuapp.com/score', data = {'word': random_tried})
    sleep(2)
    r2 = requests.post('https://cemantix.herokuapp.com/score', data = {'word': random_tried_2})

    random_similarity_1 = r.json()['score']
    random_similarity_2 = r2.json()['score']

    word_to_try = ''
    for word in model.index_to_key :
        similarity = model.similarity(word, random_tried)
        similarity_2 = model.similarity(word, random_tried_2)

        if abs(similarity - random_similarity_1) < 0.0001 and abs(similarity_2 - random_similarity_2) < 0.0001:
            print(f"Similarity for {word} is : {similarity}")
            print(f"Similarity for {word} is : {similarity_2}")
            word_to_try = word
            break

    return {
        'response': requests.post('https://cemantix.herokuapp.com/score', data = {'word': word_to_try}).json(),
        'word': word_to_try
    }

app.run()


