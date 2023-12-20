# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 12:27:30 2020

"""

from os.path import join

def get_data_path():
    return 'your own data path'  # change to your own path
        
def get_repository_file():  # sqlite database file
    return join(get_data_path(), 'repository', 'si_repository.db')  # change to your own path

