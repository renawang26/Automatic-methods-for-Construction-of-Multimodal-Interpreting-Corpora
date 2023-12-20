# -*- coding: utf-8 -*-
"""
Created on Mon Nov 4 20:27:30 2020

"""

# %%

import os
import json
from os.path import join, dirname
import intepret_db_util_git as db_util
from decimal import Decimal
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import re
import json
import pandas as pd

from datetime import datetime, timedelta
import interpret_db_util_git as db_util

from decimal import Decimal

SPEAK_START_TS_YEAR=2021

def save_recognize_result(file, student, datas, lang, lang_code, score, provider, speech, subject):

    interpret_id = db_util.insert_intepret(student, file, lang, lang_code, score, provider, speech, subject)
    if interpret_id == -1:
        print('Insert interpret fail, abort it.')
        return ''

    content_first = True

    trans = []
    sentence = ''
    sentence_st = Decimal(0.0)
    sentence_et = Decimal(0.0)
    sentence_dt = Decimal(0.0)
    sentence_lt = Decimal(0.0)
    sentence_confidence = Decimal(0.0)

    sentence_first = True

    word = ''
    word_st = Decimal(0.0)
    word_et = Decimal(0.0)
    word_dt = Decimal(0.0)
    word_lt = Decimal(0.0)
    word_confidence = Decimal(0.0)
    pre_word_et = Decimal(0.0)

    sentence_seq_no = 1
    for data in datas:
        channel_tag = ''

        for alternatives in data['alternatives']:
            word_seq_no = 1
            word_datas = []
            sentence_first = True
            sentence_confidence = alternatives['confidence']

            if lang == 'zh':
                sentence = re.sub(r'\s', '', alternatives['transcript'])
            else:
                sentence = alternatives['transcript']

            for i in range(0, len(alternatives['timestamps'])):
                word_data = {}
                word_confidence = alternatives['word_confidence'][i][1]
                # assign speaker tag
                word_speaker_tag = -1
                
                word = alternatives['timestamps'][i][0]
                word_st = Decimal(str(alternatives['timestamps'][i][1]))
                word_et = Decimal(str(alternatives['timestamps'][i][2]))
                word_dt = word_et - word_st
                word_lt = word_st - pre_word_et
                pre_word_et = word_et  # assign end time to pre end time for calculate lag time

                if content_first:
                    sentence_lt = word_st
                    content_first = False

                if sentence_first:
                    sentence_st = word_st
                    sentence_lt = word_lt
                    sentence_first = False

                word_data['seq_no'] = word_seq_no
                word_data['word'] = word
                word_data['start_time'] = word_st
                word_data['end_time'] = word_et
                word_data['duration'] = word_dt
                word_data['lag'] = word_lt
                word_data['confidence'] = word_confidence
                word_data['speaker_tag'] = word_speaker_tag
                word_data['speak_start_timestamp'] = str(pd.Timestamp('{}-01-01 00:00:00'.format(SPEAK_START_TS_YEAR)) + timedelta(seconds=float(word_st)))
                word_datas.append(word_data)

                word_seq_no = word_seq_no + 1
        
            sentence_et = word_et
            sentence_dt = sentence_et - sentence_st

            sentence_id = db_util.insert_interpret_sentence(interpret_id, file, provider, sentence_seq_no, sentence, channel_tag, lang, lang_code,
                       float(sentence_st), float(sentence_et), float(sentence_dt), float(sentence_lt), float(sentence_confidence))

            for word_data in word_datas:
                db_util.insert_interpret_sentence_detail(interpret_id, file, provider, lang, sentence_id, word_data['seq_no'], word_data['word'], 
                            float(word_data['start_time']), float(word_data['end_time']), word_data['speak_start_timestamp'], float(word_data['duration']), 
                            float(word_data['lag']), word_data['confidence'], word_speaker_tag, speech, subject)

            sentence_seq_no = sentence_seq_no + 1

            trans.append(sentence[:-1])
            break

    print('End of insert_corpus.')

    return trans

def ibm_speech_recognize(target_path, root, name, lang, interpret_subject):
    # Use IBM cloud speech to text
    # content_type: [application/octet-stream, audio/basic, audio/flac, audio/g729, audio/l16, audio/mp3, 
    #                audio/mpeg, audio/mulaw, audio/ogg, audio/ogg;codecs=opus, audio/ogg;codecs=vorbis, 
    #                audio/wav, audio/webm, audio/webm;codecs=opus, audio/webm;codecs=vorbis]
    
    # model: [ar-AR_BroadbandModel, de-DE_BroadbandModel, en-GB_BroadbandModel, en-GB_NarrowbandModel,
    #         en-US_BroadbandModel, en-US_NarrowbandModel, en-US_ShortForm_NarrowbandModel, es-ES_BroadbandModel,
    #         es-ES_NarrowbandModel, fr-FR_BroadbandModel, fr-FR_NarrowbandModel, ja-JP_BroadbandModel, 
    #         ja-JP_NarrowbandModel, ko-KR_BroadbandModel, ko-KR_NarrowbandModel, pt-BR_BroadbandModel,
    #         pt-BR_NarrowbandModel, zh-CN_BroadbandModel, zh-CN_NarrowbandModel]
    audio_file = join(root, name)
    interpret_file = '{}%{}'.format(interpret_subject, name[:name.rfind(".")])
    
    json_file = join(target_path, interpret_file + '.json')
    content_type = 'audio/' + name[name.rfind(".") + 1:]
    
    # check is destination file existed, if existed; the abort it
    if os.path.isfile(json_file):
        print('{} existed, abort covert.'.format(json_file)) 
        return False
    else:
        print('Start to convert lang:{}, content_type:{}, audio:{}, target:{}' .format(lang, content_type, audio_file, json_file))

        authenticator = IAMAuthenticator('IBM_API_KEY') # change to your own api key
        
        speech_to_text = SpeechToTextV1(authenticator=authenticator)

        url = 'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com'
        speech_to_text.set_service_url(url)

        model='en-GB_BroadbandModel'
        language='en-GB'
        
        if lang == 'zh':
            model = 'zh-CN_BroadbandModel'
            language = 'zh-CN'
                
        with open(audio_file, 'rb') as audio_stream:
            response = speech_to_text.recognize(
                audio = audio_stream,
                content_type = content_type,
                model = model,
                language = language,
                word_confidence = True,
                timestamps = True,
                inactivity_timeout = 60,
                max_alternatives = 1)
            
            if response.status_code == 200:
                json_string = json.dumps(response.result['results'], indent = 2, ensure_ascii = False)
        
                with open(json_file, 'w', encoding='utf-8') as wf:
                    wf.writelines(json_string)
            else:
                print('Speech to text reply abnormal, response.status_code:{}'.format(response.status_code))
                return False
        
    print('End of speech recognize:{}.'.format(audio_file))
    print('-' * 50)
    
    return True
    
def batch_ibm_speech_to_text(target_path, src_path, lang, interpret_subject):
    exts = ['mp3', 'flac']
    
    src_path = join(src_path, lang)
    target_path = join(target_path, lang)
    
    if not os.path.exists(src_path):
        print('Source path: {} not exist, abort request.'.format(src_path))
        return
    
    # create audio folder for save audio file if folder not existed.
    if not os.path.exists(target_path):
        print('Path:{} not exist, start to create.'.format(target_path))
        os.makedirs(target_path)
        
    for (root, dirs, names) in os.walk(src_path):
        for name in names:
            if os.path.isfile(join(root, name)):
                if(name[name.rfind(".") + 1:] in exts):
                    ibm_speech_recognize(target_path, root, name, lang, interpret_subject)
                else:
                    print('The file {} extentsion is not supported, bypass it.'.format(join(root, name)))
                    return False
            else:
                print("The {0} is not file, bypass it.".format(os.path.join(root, name)))
                return False
        
    return True

# %%
# =============================================================================
# Batch speech recognize interpretation (2 language, English and Chinese)
# =============================================================================
if __name__ == '__main__':
    langs = ('zh', 'en')
    target_path = "your own speech recognized file path" # change to your own speech recognized file save path
    src_path = "your own speech file path" # change to your own speech file path

    interpret_subject = 'your own interpret subject' # change to your own interpret subject
    
    for lang in langs:
        batch_ibm_speech_to_text(target_path, src_path, lang, interpret_subject)
        
    print("End.")
    
    
# %% 
# =============================================================================
# Save IBM speech recognize result to database
# =============================================================================

import os
import json
from os.path import join

langs = ['en', 'zh']
interpret_subject = 'your own interpret subject' # change to your own interpret subject
src_path = 'your own speech recognized result text file' # change to your own path
score = -1

for lang in langs:
    if lang == 'zh':
        language_code='zh-CN'  # en-GB|zh-CN
    elif lang == 'en':
        language_code='en-GB'
    
    for (root, dirs, names) in os.walk(join(src_path, lang)):
        for name in names:
            if(name[name.rfind(".") + 1:] in ['json']):
                print('Start to process {}/{}'.format(root, name))
                interpret_file = name[:name.find(".")]
                student_name = interpret_file[interpret_file.rfind("%") + 1:]
                
                with open(join(root, name), 'r', encoding='utf-8') as jf:
                    datas = json.load(jf)
                    save_recognize_result(interpret_file, student_name, datas, lang, language_code, score, '', 'ibm', '', interpret_subject)
            else:
                print('The file {} extentsion is not supported, bypass it.'.format(join(root, name)))
                
print("End.")
