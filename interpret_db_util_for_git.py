# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 12:27:30 2020

"""

import sqlite3
import pandas as pd
import interpret_config_git as cfg
from sqlalchemy import create_engine
from datetime import datetime

isolation_level = None  # autocommit mode

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def insert_intepret(student, file, lang, lang_code, score, provider, speech, subject):
    intepret_id = -1
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        cursor = conn.cursor()
        insert = """INSERT INTO interpret (student_name, interpret_file, lang, language_code, score, service_provider, speech, interpret_subject)
                    VALUES (:student, :file, :lang, :lang_code, :score, :provider, :speech, :subject)"""
        try:
            cursor.execute(insert, {'student': student, 'file': file, 'lang': lang,
                                    'lang_code': lang_code, 'score': score, 'provider': provider,
                                    'speech': speech, 'subject': subject})
            intepret_id = cursor.lastrowid
            cursor.close()
        except Exception as e:
            cursor.close()
            print("Exception in insert interpret, interpret_file = {}, exception = {}.".format(file, e))
            return False

    return intepret_id

def insert_interpret_sentence(interpret_id, interpret_file, service_provider, seq_no, sentence, channel_tag, lang,
                              language_code, start_time, end_time, interpret_duration, pause_duration, confidence):
    sentence_id = -1
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        cursor = conn.cursor()

        insert = """INSERT INTO interpret_sentence (interpret_id, interpret_file, service_provider, seq_no, sentence, channel_tag, lang, language_code, 
                        start_time, end_time, interpret_duration, pause_duration, confidence)
                    VALUES (:interpret_id, :interpret_file, :service_provider, :seq_no, :sentence, :channel_tag, :lang, :language_code, 
                        :start_time, :end_time, :interpret_duration, :pause_duration, :confidence)"""

        try:
            cursor.execute(insert, {'interpret_id': interpret_id, 'interpret_file': interpret_file,
                                    'service_provider': service_provider,
                                    'seq_no': seq_no, 'sentence': sentence,
                                    'channel_tag': channel_tag, 'lang': lang, 'language_code': language_code,
                                    'start_time': start_time, 'end_time': end_time,
                                    'interpret_duration': interpret_duration,
                                    'pause_duration': pause_duration, 'confidence': confidence})
            sentence_id = cursor.lastrowid
            cursor.close()
        except Exception as e:
            cursor.close()
            print("Exception in insert interpret sentence, interpret_id = {}, exception = {}.".format(interpret_id, e))
            return False
            
    return sentence_id


def insert_interpret_sentence_detail(interpret_id, interpret_file, service_provider, lang,
                                     sentence_id, seq_no, word, start_time, end_time, speak_start_timestamp,
                                     interpret_duration, pause_duration, confidence, speaker_tag, speech, interpret_subject):
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        cursor = conn.cursor()
        insert = """INSERT INTO interpret_sentence_detail (interpret_id, interpret_file, service_provider, lang, sentence_id, seq_no, word, start_time, end_time, speak_start_timestamp, interpret_duration, pause_duration, confidence, speaker_tag, speech, interpret_subject)
                    VALUES (:interpret_id, :interpret_file, :service_provider, :lang, :sentence_id, :seq_no, :word, :start_time, :end_time, :speak_start_timestamp, :interpret_duration, :pause_duration, :confidence, :speaker_tag, :speech, :interpret_subject)"""

        try:
            cursor.execute(insert, {'interpret_id': interpret_id, 'interpret_file': interpret_file,
                                    'service_provider': service_provider,
                                    'lang': lang, 'sentence_id': sentence_id, 'seq_no': seq_no, 'word': word,
                                    'start_time': start_time,
                                    'end_time': end_time, 'speak_start_timestamp': speak_start_timestamp,
                                    'interpret_duration': interpret_duration,
                                    'pause_duration': pause_duration,
                                    'confidence': confidence, 'speaker_tag': speaker_tag, 'speech': speech,
                                    'interpret_subject': interpret_subject})
            cursor.close()
        except Exception as e:
            cursor.close()
            print("Exception in insert interpret sentence detail, sentence_id = {}, word = {}, exception = {}.".format(
                sentence_id, word, e))
            return False

    return True

def update_student_score(interpret_file, student_name, mark, speech):
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        cursor = conn.cursor()

        update_ts = datetime.now()

        update = """UPDATE interpret
                    SET student_name = :student_name, score = :score, speech = :speech, update_ts = :update_ts
                    WHERE interpret_file = :interpret_file"""

        try:
            cursor.execute(update, {'student_name': student_name, 'score': mark, 'speech': speech,
                                    'interpret_file': interpret_file, 'update_ts': update_ts})
            cursor.close()
        except Exception as e:
            cursor.close()
            print("Exception in update student score, interpret_id = {}, exception = {}.".format(interpret_file, e))
            return False

    return True

def get_interpret_files(lang, provider):
    interprets = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT interpret_file, lang, service_provider, speech, 
                    interpret_subject AS subject, score AS SCORE 
                    FROM interpret WHERE lang=:lang AND service_provider = :service_provider"""

            cursor.execute(sel, {'lang': lang, 'service_provider': provider})

            interprets = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret, exception:{}.".format(e))

    return interprets

def get_phd_interpret(lang, service_provider):
    interprets = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT id AS interpret_id, interpret_file, lang, service_provider, speech, 
                    interpret_subject AS subject, score AS SCORE 
                    FROM interpret WHERE lang=:lang AND service_provider = :service_provider
                    AND interpret_file IN (
                        SELECT file_name FROM pd_phd_interpret_paraverbal
                    )"""

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            interprets = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret, exception:{}.".format(e))

    return interprets

def get_interpret(lang, service_provider, has_score=False):
    interprets = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT id AS interpret_id, interpret_file, lang, service_provider, speech, 
                    interpret_subject AS subject, score AS SCORE 
                    FROM interpret WHERE lang=:lang AND service_provider = :service_provider"""
                
            if has_score == True:
                sel = "{} SCORE > 0 ".format(sel)

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            interprets = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret, exception:{}.".format(e))

    return interprets

def get_interpret_id(interpret_file, lang, service_provider):
    intepret_id = -1
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        cursor = conn.cursor()
        conn.text_factory = str
        try:
            sel = """SELECT id
                FROM interpret
                WHERE interpret_file = :interpret_file
                AND lang = :lang AND service_provider = :service_provider"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            row = cursor.fetchone()
            if row is not None:
                intepret_id = row[0]

            cursor.close()
        except Exception as e:
            cursor.close()
            print("Exception in select interpret id, interpret_file = {}, exception:{}".format(interpret_file, e))

    return intepret_id

def get_interpret_data(interpret_file, lang, service_provider):
    interpret_data = {}
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory

        cursor = conn.cursor()

        try:
            sel = """SELECT id, student_name, interpret_file, lang, score, comment, interpret_subject, speech
                    FROM interpret
                    WHERE interpret_file = :interpret_file
                    AND lang = :lang AND service_provider = :service_provider"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            interpret_data = cursor.fetchone()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret words, interpret_file:{}, exception:{}.".format(interpret_file, e))

    return interpret_data

def get_sentence_ids(interpret_file, lang, service_provider):
    sentence_ids = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT s.id as sentence_id
                    FROM interpret i, interpret_sentence s
                    WHERE i.id = s.interpret_id
                    AND i.interpret_file = :interpret_file AND i.lang = :lang AND i.service_provider = :service_provider
                    ORDER BY sentence_id ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            sentence_ids = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select sentence ids, interpret_file = %s, exception:%s" % (interpret_file, e))

    return sentence_ids

def get_all_interpret_sentences(lang, service_provider):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT i.id AS interpret_id, i.interpret_file, s.seq_no, s.id as sentence_id, s.sentence, s.start_time, s.end_time, s.interpret_duration, 
                    s.pause_duration, s.confidence
                    FROM interpret i, interpret_sentence s
                    WHERE i.id = s.interpret_id
                    AND i.lang = :lang AND i.service_provider = :service_provider
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select all sentences, exception:{}.".format(e))

    return sentences

def get_sentences_from_interpret_id(interpret_id):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT seq_no, id as sentence_id, sentence, start_time, end_time, interpret_duration, 
                    pause_duration, confidence
                    FROM interpret_sentence
                    WHERE interpret_id = :interpret_id
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'interpret_id': interpret_id})

            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("get_sentences_from_interpret_id catch exception, interpret_id:{}, ex:{}.".
                  format(interpret_id, e))

    return sentences

def get_interpret_sentences(interpret_file, lang, service_provider):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT seq_no, id as sentence_id, sentence, start_time, end_time, interpret_duration, 
                    pause_duration, confidence
                    FROM interpret_sentence
                    WHERE interpret_file = :interpret_file 
                    AND lang = :lang AND service_provider = :service_provider
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})
            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print(
                "Exception in select interpret sentences, interpret_file:{}, lang:{}, service_provider:{}, "
                "exception:{}.".
                format(interpret_file, lang, service_provider, e))

    return sentences

def get_simultaneous_interpret_sentences_time(interpret_file, service_provider):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file('simultaneous_interpretation')) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT sentence_seq_no AS seq_no, min(speak_start_time) AS start_time, max(speak_end_time) AS end_time
                    FROM pd_interpret_words
                    GROUP BY interpret_file, sentence_seq_no 
                    HAVING interpret_file = :interpret_file 
                    AND service_provider = :service_provider
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'service_provider': service_provider})

            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print(
                "Exception in select interpret sentences, interpret_file:{}, service_provider:{}, "
                "exception:{}.".
                format(interpret_file, service_provider, e))

    return sentences

def get_interpret_edit_sentences(interpret_file, lang, service_provider):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT seq_no, sentence, confidence, edit_sentence, lang, service_provider
                    FROM interpret_edit
                    WHERE interpret_file = :interpret_file 
                    AND lang = :lang AND service_provider = :service_provider
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            print('get_interpret_edit_sentences', sel, interpret_file, lang, service_provider)
            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print(
                "Exception in select interpret sentences, interpret_file:{}, lang:{}, service_provider:{}, "
                "exception:{}.".
                format(interpret_file, lang, service_provider, e))

    return sentences

def get_interpret_file_filter_score(lang, service_provider, has_score):
    interpret_files = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        relation = '>='
        if has_score is False:
            relation = '<'

        try:
            sel = """SELECT * FROM pd_interpret_paraverbal
                        WHERE lang = :lang AND service_provider = :service_provider
                        AND SCORE {} 0
                        ORDER BY interpret_file ASC""".format(relation)

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            results = cursor.fetchall()
            for result in results:
                interpret_files.append(result['interpret_file'])

            cursor.close()
        except Exception as e:
            print(
                "get_interpret_paraverbal fail, lang={}, service_provider={}, ex:{}".format(lang, service_provider, e))

    return interpret_files


# this function reply the edit word group by sentence
def get_interpret_edit_word_sentences(interpret_file, lang, service_provider):
    sentences = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        separator = ''
        if lang == 'en':
            separator = ' '

        try:
            sel = """SELECT sentence_seq_no As Seq, edit_order, GROUP_CONCAT(IIF(edit_word='', null, edit_word), :separator ) AS Sentence
                   FROM pd_interpret_words 
                   GROUP BY interpret_file, sentence_seq_no
                   HAVING interpret_file = :interpret_file
                   AND lang = :lang AND service_provider = :service_provider
                ORDER BY sentence_seq_no, edit_order ASC"""

            cursor.execute(sel, {'separator': separator, 'interpret_file': interpret_file, 'lang': lang,
                                 'service_provider': service_provider})

            print('get_interpret_edit_word_sentences', sel, separator, interpret_file, lang, service_provider)
            sentences = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in get_interpret_edit_word_sentences, {}, {}, {}, ex:{}.".format(interpret_file, lang,
                                                                                              service_provider, e))

    return sentences


def get_interpret_paraverbal(interpret_file, lang, service_provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT * FROM pd_interpret_words
                    WHERE interpret_file = :interpret_file AND lang = :lang AND service_provider = :service_provider                    
                    ORDER BY sentence_seq_no, word_seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            print(sel, interpret_file, lang, service_provider)
            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret words, interpret_file:{}, exception:{}.".format(interpret_file, e))

    return words

def get_pd_interpret_words(interpret_file, service_provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT interpret_id, interpret_file, lang, speech, sentence_seq_no, word_seq_no, word, interpret_duration, speak_start_timestamp 
                    FROM pd_interpret_words
                    WHERE interpret_file = :interpret_file AND service_provider = :service_provider
                    ORDER BY speak_start_timestamp ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'service_provider': service_provider})

            print(sel, interpret_file, service_provider)
            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select pd_interpret_words, interpret_file:{}, exception:{}.".format(interpret_file, e))

    return words

def get_interpret_words(interpret_file, lang, service_provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT s.interpret_file, s.id AS setence_id, s.seq_no AS sentence_seq_no,
                        isd.seq_no AS word_seq_no, isd.word, isd.start_time, isd.end_time, 
                        isd.interpret_duration, isd.pause_duration, isd.confidence,
                        isd.speak_start_timestamp
                    FROM interpret_sentence s, interpret_sentence_detail isd
                    WHERE s.id = isd.sentence_id
                    AND s.interpret_file = :interpret_file AND s.lang = :lang AND s.service_provider = :service_provider
                    AND s.interpret_file = isd.interpret_file
                    ORDER BY sentence_seq_no, word_seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file, 'lang': lang, 'service_provider': service_provider})

            print(sel, interpret_file, lang, service_provider)
            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret words, interpret_file:{}, exception:{}.".format(interpret_file, e))

    return words

def get_phd_interpret_sentence_paraverbal(lang, service_provider):
    sent_paraverbal = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            sel = """SELECT interpret_id, interpret_file, sentence_seq_no, AVG(confidence) AS confidence_AVG, SUM(NFP) AS NFP_SUM, 
                    SUM(NRLUP) AS NRLUP_SUM, SUM(NPLUP) AS NPLUP_SUM, SUM(NUP) AS NUP_SUM, SUM(NRSA) AS NRSA_SUM, 
                    SUM(NPSA) AS NPSA_SUM, SUM(NMUC) AS NMUC_SUM, SUM(NEUC) AS NEUC_SUM, count(*) AS word_count
                    FROM pd_phd_file_interpret_words_zh_ibm ppfiwzi 
                    WHERE lang = :lang AND service_provider = :service_provider
                    GROUP BY interpret_file, sentence_seq_no
                """

            print(sel, lang, service_provider)

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            sent_paraverbal = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select all interpret words, exception:{}.".format(e))

    return sent_paraverbal

def get_phd_interpret_all_words(lang, service_provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT i.id AS interpret_id, i.lang, i.interpret_file, i.speech,
                    s.seq_no AS sentence_seq_no, isd.seq_no AS word_seq_no, isd.word, 
                    isd.start_time AS speak_start_time, isd.end_time AS speak_end_time,
                    isd.interpret_duration, isd.pause_duration, isd.pause_duration as adjust_pause_duration, 
                    isd.confidence, i.score AS SCORE
                FROM interpret i, interpret_sentence s, interpret_sentence_detail isd
                WHERE i.id = s.interpret_id AND s.id = isd.sentence_id
                AND i.interpret_file IN (
                SELECT file_name FROM pd_phd_interpret_paraverbal
                )
                AND i.lang = :lang AND i.service_provider = :service_provider
                """

            print(sel, lang, service_provider)

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select all interpret words, exception:{}.".format(e))

    return words

def get_interpret_all_words(lang, service_provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT i.id AS interpret_id, i.lang, i.interpret_file, i.speech,
                        s.seq_no AS sentence_seq_no, isd.seq_no AS word_seq_no, isd.word, 
                        isd.start_time AS speak_start_time, isd.end_time AS speak_end_time,
                        isd.interpret_duration, isd.pause_duration, isd.pause_duration as adjust_pause_duration, 
                        isd.confidence, i.score AS SCORE
                    FROM interpret i, interpret_sentence s, interpret_sentence_detail isd
                    WHERE i.id = s.interpret_id AND s.id = isd.sentence_id 
                    AND i.lang=:lang AND i.service_provider = :service_provider"""

            print(sel, lang, service_provider)

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select all interpret words, exception:{}.".format(e))

    return words

def get_sentence_words(sentence_id):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT sentence_id, seq_no, word, start_time, end_time, interpret_duration, pause_duration, confidence,
                    edit_sentence_id, edit_seq_no, edit_word
                    FROM interpret_sentence_detail 
                    WHERE sentence_id = :sentence_id
                    ORDER BY seq_no ASC"""

            cursor.execute(sel, {'sentence_id': sentence_id})

            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select sentence words, sentence_id = {}, exception:{}.".format(sentence_id, e))
    return words

def get_interpret_sentence_detail(interpret_file, provider):
    words = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT sentence_id, seq_no, word, confidence, speak_start_timestamp
                    FROM interpret_sentence_detail 
                    WHERE interpret_file = :interpret_file
                    ORDER BY sentence_id, seq_no ASC"""

            cursor.execute(sel, {'interpret_file': interpret_file})

            words = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret_file words, interpret_file = {}, exception:{}.".format(interpret_file, e))
    return words


def store_db_pandas(df, table, action):  # action {‘fail’, ‘replace’, ‘append’}, default ‘fail’

    engine = create_engine('sqlite:///{}'.format(cfg.get_repository_file()))

    df.to_sql(table, con=engine, if_exists=action)


def read_db_pandas(table):
    engine = create_engine('sqlite:///{}'.format(cfg.get_repository_file()))

    return pd.read_sql_table(table, con=engine)

def get_interpret_features(lang, provider):
    interprets = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT interpret_file, lang, service_provider, speech, 
                    interpret_subject AS subject, score AS SCORE 
                    FROM interpret WHERE lang=:lang AND service_provider = :service_provider"""

            cursor.execute(sel, {'lang': lang, 'service_provider': provider})

            interprets = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret, exception:{}.".format(e))

    return interprets

def get_interpret_doc_sentence(lang, service_provider):
    interprets = []
    with sqlite3.connect(cfg.get_repository_file()) as conn:
        conn.text_factory = str
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        try:
            sel = """SELECT id AS interpret_id, interpret_file, lang, service_provider, speech, 
                    interpret_subject AS subject, score AS SCORE 
                    FROM interpret WHERE lang=:lang AND service_provider = :service_provider"""

            cursor.execute(sel, {'lang': lang, 'service_provider': service_provider})

            interprets = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print("Exception in select interpret, exception:{}.".format(e))

    return interprets