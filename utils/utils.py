import time

import requests
import os
import psycopg2

from datetime import datetime
from time import sleep
from gensim.models import KeyedVectors


def guess_word(word):
    req = requests.post('https://cemantix.herokuapp.com/score', data={'word': word}).json()
    sleep(2.0)
    if 'score' in req:
        return req['score']

    return -1000


def save_to_db(word_found, index_history, start_search):
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')

    sql = """INSERT INTO history(date, word, index_history, time_to_resolution, algorithm_version) """ + \
          """values (%s, %s, %s, %s, %s);"""

    cur = conn.cursor()
    cur.execute(sql, (datetime.now(), word_found, index_history, time.process_time() - start_search, 1))

    conn.commit()
    cur.close()


def get_todays_row():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')

    sql = """SELECT * FROM history order by date DESC limit 1"""

    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()

    conn.commit()
    cur.close()

    return row


def get_all_rows():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')

    sql = """SELECT * FROM history order by date DESC"""

    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchall()

    conn.commit()
    cur.close()

    return row


def get_today_s_word(starter):
    guess = guess_word(starter)
    print("Loading model")
    model = KeyedVectors.load_word2vec_format(
        "https://embeddings.net/embeddings/frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin",
        binary=True,
        unicode_errors="ignore"
    )
    print("Model loaded")

    word_tried = [{'word': starter, 'guess': guess}]

    print("Loading word_filtered")
    with open('word_filtered.txt', 'r', encoding='utf-8') as file:
        word_filtered = file.read().split(',')
    print("Word filtered loaded")

    similarity_to_know_words = [{
        'word': word,
        'guess': 0,
    } for word in word_filtered]

    similarities_history = []

    start_search = time.process_time()
    while guess < 1:
        current_similarity_to_known_words = [{
            'word': word,
            'guess': abs(guess - model.similarity(word_tried[-1]['word'], word))
        } for word in word_filtered]

        similarity_to_know_words = [{
            'word': x['word'],
            'guess': x['guess'] + y['guess']
        } for x, y in zip(current_similarity_to_known_words, similarity_to_know_words)]

        sorted_similarity_to_know_words = sorted(similarity_to_know_words, key=lambda s: s['guess'])

        print(f"Trying word : {sorted_similarity_to_know_words[0]['word']}")
        guess = guess_word(sorted_similarity_to_know_words[0]['word'])
        print(f"Similarity is : {guess}")
        similarities_history.append(sorted_similarity_to_know_words)
        word_tried.append({'word': sorted_similarity_to_know_words[0]['word'], 'guess': guess})

    word_found = word_tried[-1]['word']

    index_history = [list(map(lambda l: l['word'], history)).index(word_found) for history in similarities_history]

    save_to_db(word_found, str(index_history), start_search)

    return f"Trouvé ! {word_found}. Index history is : {index_history}"
