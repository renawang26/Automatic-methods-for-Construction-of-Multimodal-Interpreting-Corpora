# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 23:36:45 2021

"""

# %%
import re
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import interpret_db_util_git as db_util
from IPython.display import display
from IPython.core.display import display, HTML
import nltk
from nltk.util import ngrams
from pandas import Series, DataFrame, merge

from string import punctuation
from nltk.util import ngrams

from nltk.tokenize import SyllableTokenizer
from nltk import word_tokenize

from zhon.hanzi import punctuation

SSP = SyllableTokenizer()

SPEAK_START_TS_YEAR=2021

def remove_punctuation(line, strip_all = False):
    if strip_all:
        rule = re.compile(u"[^a-zA-Z0-9\u4e00-\u9fa5]")
        line = rule.sub('', line)
    else:
        remove_punctuation = punctuation + " , "
        line = re.sub(r"[%s]+" % remove_punctuation, "", line)
        
    line = ' '.join(line.split())
    
    return line.strip()

def get_syllable_interpret(arr, syllable_len, interpret_duration):
    if arr[syllable_len] == 0:
        print(arr[interpret_duration], arr[syllable_len])
    return arr[interpret_duration] / arr[syllable_len]

def set_subject(x):
    tokens = x.split('%')
    if len(tokens) == 2:
        return tokens[0]
    elif len(tokens) > 2:
        return '%'.join(tokens[:2])
    return x

def set_speak_start_timestamp(speak_start_time):
    start_time = pd.Timestamp('{}-01-01 00:00:00'.format(SPEAK_START_TS_YEAR))
    return start_time + timedelta(seconds=speak_start_time)

# Function to generate n-grams from sentences.
def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [' '.join(grams) for grams in n_grams]

def mark_unfilled_NUP_pause(arr, sentence_seq_no, word_seq_no, pause_duration, filled_pause):
    # if filled puase existed; then bypass pause
    if arr[filled_pause] == 'NFP':
        return ''
    # bypass the 1st pause in article
    if arr[sentence_seq_no] == 1 and arr[word_seq_no] == 1:
        return ''
    if arr[pause_duration] > 0.25:
        return 'NUP'
    return ''

def get_symbol_summary(df, category):
    df_sub = df[df[category].str.len() > 0]
    df_sum = df_sub.groupby(['interpret_id', category])[
        category].count().reset_index(name='count')

    df_pv = pd.pivot_table(df_sum, index=['interpret_id'], columns=[
                           category], values=['count'], fill_value=0)
    df_pv.columns = [str(s2) for (s1, s2) in df_pv.columns.tolist()]
    df_pv.reset_index(inplace=True)

    return df_pv

def get_interpret_statistics(df_sub):
    desc = df_sub.describe()
    iqr = desc['75%'] - desc['25%']

    upper_mild_outlier = desc['75%'] + (iqr * 1.5)
    upper_extreme_outlier = desc['75%'] + (iqr * 3)

    lower_mild_outlier = desc['25%'] - (iqr * 1.5)
    lower_extreme_outlier = desc['25%'] - (iqr * 3)
    return desc, iqr, lower_mild_outlier, lower_extreme_outlier, upper_mild_outlier, upper_extreme_outlier

def get_syllable_en(word):
    syllable = ''
    try:
        syllables = []
        word = remove_punctuation(word, True)
        for word_token in word_tokenize(word):
            if word_token.isalpha():
          #      print(word_token)
                syllables.append([SSP.tokenize(token) for token in word_tokenize(word_token)][0])

        for syl in syllables:
            syllable = '{} {}'.format(syllable, ' '.join(syl))
    except:
        print("get_syllable_en catch exception, word:{}, exp:{}".format(word, e))
        syllable = str(word)
    
    return syllable.strip()

def get_syllable_len_zh(syllable):
    syllable_len = 1
    if syllable.isalpha() == True:
        syllable_len = len(syllable)
        
    if syllable_len == 0:
        print(syllable)
    
    return syllable_len

def get_syllable_len_en(syllable):
    syllable_len = len(syllable.split())
        
    if syllable_len == 0:
        print(syllable)
    
    return syllable_len

def get_interpret_paraverbal(lang, service_provider, table_if_exists_action):
    filled_strings: str = ''
    if lang == 'zh':
        filled_strings = ['啊', '嗯', '呃', '哦']
    elif lang == 'en':
        filled_strings = ['%HESITATION']
        
    def mark_filled_pause_zh(x):
        if str(x).isalpha():
            for idx in range(0, len(x)):
                if x[idx] in filled_strings:
                    return 'NFP'
        return ''

    def mark_filled_pause_en(x):
     #   if str(x).isalpha():    
        if x in filled_strings:
            return 'NFP'
        return ''
    
    words = db_util.get_interpret_all_words(lang, service_provider)
    
    if len(words) > 0:
        df_word = pd.DataFrame.from_dict(words)
        df_word['lang'] = lang
        df_word['service_provider'] = service_provider
        df_word["subject"] = df_word["interpret_file"].map(set_subject)
        
        interpret = db_util.get_interpret(lang, service_provider)
        df_interpret = pd.DataFrame.from_dict(interpret)
        
        db_util.store_db_pandas(df_interpret, 'pd_interpret_score_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        if lang == 'zh':
            df_word['syllable'] = df_word['word'].apply(lambda x: str(x))
            df_word['syllable_len'] = df_word['syllable'].map(get_syllable_len_zh)
        else:
            df_word['syllable'] = df_word['word'].map(get_syllable_en)
            df_word['syllable_len'] = df_word['syllable'].map(get_syllable_len_en)
        
        df_word['syllable_interpret'] = df_word[['syllable_len', 'interpret_duration']].apply(get_syllable_interpret, axis=1, args=('syllable_len', 'interpret_duration'))
        
        df_word['speak_start_time'] = df_word['speak_start_time'].astype(float)
        df_word['speak_start_timestamp'] = df_word['speak_start_time'].map(set_speak_start_timestamp)
        
        boxplot = []
        sdesc, siqr, lmsl, lesl, umsl, uesl = get_interpret_statistics(df_word['syllable_interpret'])
        
        tmp = sdesc.tolist()
        tmp.insert(0, 'Syllable Speak Duration')
        tmp.insert(1, lang)
        tmp.insert(2, service_provider)
        tmp.extend([siqr, lmsl, lesl, umsl, uesl])
        boxplot.append(tmp)
        
        # calcuate pause outliner, ignore puase duration is 0 cases
        df_pause_all = df_word.query('pause_duration > 0')
        df_pause_1 = df_word.query('pause_duration > 0 and sentence_seq_no == 1 and word_seq_no == 1')
        df_pause = pd.concat([df_pause_all, df_pause_1]).drop_duplicates(keep=False)  # drop 1st sentence 1st pause
        
        db_util.store_db_pandas(df_pause, 'pd_interpret_pause_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        pdesc, piqr, lmpl, lepl, umpl, uepl = get_interpret_statistics(df_pause['pause_duration'])
        
        tmp = pdesc.tolist()
        tmp.insert(0, 'Unfilled Pause Duration')
        tmp.insert(1, lang)
        tmp.insert(2, service_provider)
        tmp.extend([piqr, lmpl, lepl, umpl, uepl])
        boxplot.append(tmp)
        
        cdesc, ciqr, lmcl, lecl, umcl, uecl = get_interpret_statistics(df_word['confidence'])
        
        tmp = cdesc.tolist()
        tmp.insert(0, 'Speech To Text Confidence')
        tmp.insert(1, lang)
        tmp.insert(2, service_provider)
        tmp.extend([ciqr, lmcl, lecl, umcl, uecl])
        boxplot.append(tmp)
        
        df_boxplot = pd.DataFrame(boxplot, columns=['Category', 'lang', 'service_provider', 'Count', 'Mean', 'STD', 'Min', '25%', '50%', '75%',
                                                    'Max', 'IQR', 'Lower Mild Outlier', 'lower Extreme Outlier', 'Upper Mild Outlier', 'Upper Extreme Outlier'])
        
        db_util.store_db_pandas(df_boxplot, 'pd_interpret_boxplot_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        def mark_tempo(arr, syllable_len, interpret_duration, filled_pause):
            # if filled puase existed; then bypass tempo
          #  print(arr[interpret_duration], arr[syllable_len] , lmsl, lesl, umsl, uesl)
            if arr[filled_pause] == 'NFP':
                return ''
            if arr[interpret_duration] < lmsl * arr[syllable_len] and arr[interpret_duration] >= lesl * arr[syllable_len]:
                return 'NRQA'
            if arr[interpret_duration] < lmsl * arr[syllable_len]:
                return 'NPQA'
            if arr[interpret_duration] > umsl * arr[syllable_len] and arr[interpret_duration] <= uesl * arr[syllable_len]:
                return 'NRSA'
            if arr[interpret_duration] > uesl * arr[syllable_len]:
                return 'NPSA'
            return ''
        
        def mark_clarify(x):
            if x <= lecl:
                return 'NEUC'
            if x <= lmcl and x > lecl:
                return 'NMUC'
            return ''
        
        def mark_unfilled_pause(arr, sentence_seq_no, word_seq_no, pause_duration, filled_pause):
            # if filled puase existed; then bypass pause
            if arr[filled_pause] == 'NFP':
                return ''
            # bypass the 1st pause in article
            if arr[sentence_seq_no] == 1 and arr[word_seq_no] == 1:
                return ''
            if arr[pause_duration] > uepl:
                return 'NPLUP'
            if arr[pause_duration] > umpl and arr[pause_duration] <= uepl:
                return 'NRLUP'
            return ''

        if lang == 'zh':
            df_word["filled_pause"] = df_word["word"].map(mark_filled_pause_zh)
        elif lang == 'en':
            df_word["filled_pause"] = df_word["word"].map(mark_filled_pause_en)
        
        df_word["unfilled_pause"] = df_word[['sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause']].apply(mark_unfilled_pause, axis=1,
                                                                                                                     args=('sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause'))
        df_word["unfilled_NUP_pause"] = df_word[['sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause']].apply(mark_unfilled_NUP_pause, axis=1,
                                                                                                                         args=('sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause'))
        # if unfilled pause follow by filled pause; then change filled pause to unfilled pause and sum the pause duration
        for index, row in df_word.iterrows():
            if 'UP' in row['unfilled_pause'] or 'UP' in row['unfilled_NUP_pause']:
                if df_word.at[index-1, 'filled_pause'] == 'NFP':
                    df_word.at[index-1, 'filled_pause'] = ''
                    df_word.at[index-1, 'adjust_pause_duration'] = 0
                    df_word.at[index, 'adjust_pause_duration'] = row['pause_duration'] + df_word.at[index-1, 'pause_duration']
        
        df_word['NFP'] = df_word['filled_pause'].apply(lambda x: 1 if x == 'NFP' else np.nan)
        df_pv_filled_pause = get_symbol_summary(df_word, 'filled_pause')
        df_interpret_paraverbal = merge(df_interpret, df_pv_filled_pause, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        # assign unfilled_pause base on adjust_pause_duration
        df_word["unfilled_pause"] = df_word[['sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause']].apply(mark_unfilled_pause, axis=1,
                                                                                                                     args=('sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause'))
        df_word['NRLUP'] = df_word['unfilled_pause'].apply(lambda x: 1 if x == 'NRLUP' else np.nan)
        df_word['NPLUP'] = df_word['unfilled_pause'].apply(lambda x: 1 if x == 'NPLUP' else np.nan)
        df_pv_unfilled_pause = get_symbol_summary(df_word, 'unfilled_pause')
        
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_pv_unfilled_pause, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        # assign unfilled_NUP_pause base on adjust_pause_duration
        df_word["unfilled_NUP_pause"] = df_word[['sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause']].apply(mark_unfilled_NUP_pause, axis=1,
                                                                                                                         args=('sentence_seq_no', 'word_seq_no', 'adjust_pause_duration', 'filled_pause'))
        df_word['NUP'] = df_word['unfilled_NUP_pause'].apply(lambda x: 1 if x == 'NUP' else np.nan)
        df_pv_unfilled_NUP_pause = get_symbol_summary(df_word, 'unfilled_NUP_pause')
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_pv_unfilled_NUP_pause, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        df_word['tempo'] = df_word[['syllable_len', 'interpret_duration', 'filled_pause']].apply(mark_tempo, axis=1, args=('syllable_len', 'interpret_duration', 'filled_pause'))
        
        df_word['NRSA'] = df_word['tempo'].apply(lambda x: 1 if x == 'NRSA' else np.nan)
        df_word['NPSA'] = df_word['tempo'].apply(lambda x: 1 if x == 'NPSA' else np.nan)
        df_word['NRQA'] = df_word['tempo'].apply(lambda x: 1 if x == 'NRQA' else np.nan)
        df_word['NPQA'] = df_word['tempo'].apply(lambda x: 1 if x == 'NPQA' else np.nan)
        df_pv_tempo = get_symbol_summary(df_word, 'tempo')
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_pv_tempo, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        df_word['clarity'] = df_word['confidence'].map(mark_clarify)
        df_word['NMUC'] = df_word['clarity'].apply(lambda x: 1 if x == 'NMUC' else np.nan)
        df_word['NEUC'] = df_word['clarity'].apply(lambda x: 1 if x == 'NEUC' else np.nan)
        
        df_pv_clarity = get_symbol_summary(df_word, 'clarity')
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_pv_clarity, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        df_mean_silent_pause = df_word.loc[(df_word.NUP == 1)].groupby('interpret_id')['adjust_pause_duration'].mean().to_frame('MLUP')   # silent_pause_mean
        
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_mean_silent_pause, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        df_mean_filled_pause = df_word.loc[(df_word.NFP == 1)].groupby('interpret_id')['adjust_pause_duration'].mean().to_frame('MLFP')   # filled_pause_mean
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_mean_filled_pause, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        # repair
        words = df_word.groupby("interpret_id")['word'].apply(lambda tags: ' '.join(tags))
        sent_seq_nos = df_word.groupby("interpret_id")['sentence_seq_no'].apply(
            lambda tags: ' '.join(tags.astype(str)))
        word_seq_nos = df_word.groupby("interpret_id")['word_seq_no'].apply(
            lambda tags: ' '.join(tags.astype(str)))
        
        repair = []
        for interpret_id, word in words.iteritems():
            word_grams = extract_ngrams(word, 2)
            sent_seq_grams = extract_ngrams(sent_seq_nos[interpret_id], 2)
            word_seq_grams = extract_ngrams(word_seq_nos[interpret_id], 2)
            for word_gram, sent_seq_gram, word_seq_gram in zip(word_grams, sent_seq_grams, word_seq_grams):
                word_tokens = word_gram.split(' ')
                if word_tokens[0] == word_tokens[1]:
                    repair.append([interpret_id, int(sent_seq_gram.split(
                        ' ')[1]), int(word_seq_gram.split(' ')[1]), 'NR'])
                    
        df_repair = pd.DataFrame.from_records(repair, columns=['interpret_id', 'sentence_seq_no', 'word_seq_no', 'repair'])
        df_word = pd.merge(df_word, df_repair, how='outer', on=['interpret_id', 'sentence_seq_no', 'word_seq_no'])
        df_word['NR'] = df_word['repair'].apply(lambda x: 1 if x == 'NR' else np.nan)
        df_pv_repair = get_symbol_summary(df, 'repair')
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_pv_repair, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        # calculate articulation rate, skip filled pause and longer than 0.25 seconds
        all_speak_sum = df_word.groupby('interpret_id')['interpret_duration'].sum()
        exclude_filled_pause_speak_sum = df_word.loc[(df_word.NFP != 1)].groupby('interpret_id')['interpret_duration'].sum()
        all_pause_sum = df_word.groupby('interpret_id')['adjust_pause_duration'].sum()
        exclude_NUP_pause_sum = df_word.loc[(df_word.NUP != 1)].groupby('interpret_id')['adjust_pause_duration'].sum()
        word_sum = df_word.groupby('interpret_id')['syllable_len'].sum()
        
        df_articulation_rate = word_sum.div((exclude_filled_pause_speak_sum + exclude_NUP_pause_sum), fill_value=0).to_frame('AR')  # articulation_rate
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_articulation_rate, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        df_speech_rate = word_sum.div((exclude_filled_pause_speak_sum + all_pause_sum), fill_value=0).to_frame('SR')  # speech_rate
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_speech_rate, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        # PTR, Phonation Time Ratio, speak duraiton / totl duration
        df_ptr = all_speak_sum.div((all_speak_sum + all_pause_sum), fill_value=0).to_frame('PTR')
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_ptr, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        # MLR (Mean Length of Runs), average of all speak duration between >= 0.25 seconds pause
        # ALP (Average Length of Pause), average of all speak duration between >= 0.25 seconds pause
        mlr_alp_lst = []
        ids = df_word.groupby('interpret_id')['interpret_id'].apply(lambda x: list(np.unique(x)))
        for interpret_id, value in ids.items():
            mlr_alp_dict = {}
            pre_pause_mlr = False
            mlr_cnt = 0
            mlr_len = 0
            word_cnt = 0
            df_sub = df_word[df_word['interpret_id'] == interpret_id]
            df_len = len(df_sub)
            for index_sub, row in df_sub.iterrows():
                if index_sub == 0 and row['pause_duration'] > 0:  # bypass first pause
                    continue
                word_cnt = word_cnt + 1
                if df_len == word_cnt:  # bypass last pause
                    break
                if row['pause_duration'] >= 0.25 and pre_pause_mlr:
                    mlr_cnt = mlr_cnt + 1
                    mlr_len = mlr_len + row['pause_duration']
                    pre_pause_mlr = False
                    continue
        
                if row['pause_duration'] >= 0.25:
                    pre_pause_mlr = True
        
            mlr_alp_dict['interpret_id'] = interpret_id
            mlr_alp_dict['MLR'] = mlr_cnt/word_cnt
            mlr_alp_dict['ALP'] = mlr_len/mlr_cnt
        
            mlr_alp_lst.append(mlr_alp_dict)
        
        df_mlr_alp = pd.DataFrame.from_dict(mlr_alp_lst)
        df_interpret_paraverbal = merge(df_interpret_paraverbal, df_mlr_alp, on="interpret_id", how="outer", suffixes=('_a', '_b'))
        
        if 'NFP' not in df_interpret_paraverbal.columns:
            df_interpret_paraverbal['NFP'] = np.nan
            
        db_util.store_db_pandas(df_interpret_paraverbal, 'pd_interpret_paraverbal_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        df_interpret_paraverbal_score = df_interpret_paraverbal[(df_interpret_paraverbal.SCORE > 0)]
        df_interpret_paraverbal_score_desc = df_interpret_paraverbal_score.iloc[:, 4:].describe()
        df_interpret_paraverbal_score_desc['lang'] = lang
        df_interpret_paraverbal_score_desc['service_provider'] = service_provider
        df_interpret_paraverbal_score_desc["subject"] = df_word["interpret_file"].map(set_subject)
        
        db_util.store_db_pandas(df_interpret_paraverbal_score_desc, 'pd_interpret_paraverbal_desc_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        pd.options.display.max_rows = 8
        pd.options.display.html.border = 1
        pd.options.display.precision = 2
        
        display(HTML('<span style="color:#4876FF"><h3>Interpret Data</h3></span>'))
        display(df_interpret)
        
        df_interpret_grp = df_interpret.groupby(['lang', 'service_provider', 'subject', 'speech']).size().reset_index(name='count')
        
        display(HTML('<span style="color:#4876FF"><h3>Interpret Subject/Speech</h3></span>'))
        display(df_interpret_grp)
        db_util.store_db_pandas(df_interpret_grp, 'pd_interpret_subject_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        display(HTML('<span style="color:#4876FF"><h3>Word Level Speech To Text Data</h3></span>'))
        display(df_word[['interpret_file', 'speak_start_timestamp', 'speech', 'SCORE', 'sentence_seq_no', 'word_seq_no', 'word', 'syllable', 'syllable_len',
                    'confidence', 'speak_start_time', 'speak_end_time', 'interpret_duration', 'adjust_pause_duration']])
        
        db_util.store_db_pandas(df_word, 'pd_interpret_words_{}_{}'.format(lang, service_provider), table_if_exists_action)
        
        print('Count NFP:{}, NUP:{}, NPLUP:{}, NRLUP:{}'.format(df_word[(df_word.NFP == 1)].shape[0], df_word[(df_word.NUP == 1)].shape[0], df_word[(df_word.NPLUP == 1)].shape[0], df_word[(df_word.NRLUP == 1)].shape[0]))
        
        print('word len sum:{}'.format(df_word['syllable_len'].sum()))
        print('Speak sum:{} seconds, {} minutes'.format(round(df_word['interpret_duration'].sum(), 1), round(df_word['interpret_duration'].sum()/60, 1)))
              
        print('Pause sum:{} seconds, {} minutes'.format(round(df_word['adjust_pause_duration'].sum(), 1), round(df_word['adjust_pause_duration'].sum()/60, 1)))
        
    else:
        print('Query interpret words reply no data, lang:{}, service_provider:{}, abort request.'.format(lang, service_provider))

# =============================================================================
# get_interpret_paraverbal for Chinese and English
# =============================================================================

if __name__ == '__main__':
    langs = ['zh']  # 'zh', 'en'
    service_provider = 'ibm'
    table_if_exists_action = 'replace'  # {'fail', 'replace', 'append'}, default 'fail'

    for lang in langs:
        print(lang, service_provider)
        get_interpret_paraverbal(lang, service_provider, table_if_exists_action)
            
    print('End of get_interpret_paraverbal')