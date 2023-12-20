# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 12:27:30 2020

"""

from os.path import join

def get_data_path():
    return 'your own data path'  # change to your own path
        
def get_repository_file():  # sqlite database file
    return join(get_data_path(), 'repository', 'si_repository.db')  # change to your own path

# assign pause threshold in seconds
def get_pause_threshold():
    return 1.5

# assign long pause threshold in seconds
def get_long_pause_threshold():
    return 3

# assign tempo slow threshold, in percentage of average
def get_tempo_slow_threshold():
    return 2

# assign tempo slow threshold, in percentage of average
def get_tempo_quick_threshold():
    return 0.6

