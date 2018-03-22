# Processes monthly threads files

import numpy as np 
import os
import csv
import ast 
from tqdm import tqdm
import yaml
import time
import gc
import bz2
import json
import pickle

import pdb
def merge_threads(subreddit, starting_year, starting_month, ending_year, ending_month):
   
    os.chdir('/Users/vivonasg/Documents/MSCAC_FALL_2017/SEMESTER_2/CSC2552/Exploring_Reddit')
    os.chdir('threads')
    os.chdir(subreddit)

    # load all threads data

    monthly_threads = []

    for year in range(2016, 2016 + 1):
        if starting_year == ending_year:
            first_month = starting_month
            last_month = ending_month
        else:
            if year == starting_year:
                first_month = starting_month
                last_month = 12
            elif year == ending_year:
                first_month = 1
                last_month = ending_month
            else:
                first_month = 1
                last_month = 12
        for month in range(first_month, last_month + 1):
            file = '{}_threads_{}_{}.npy'.format(subreddit, year, month)
            with open(file, 'rb') as fp:
                all_threads = pickle.load(fp)  
                monthly_threads.append(all_threads) 

    # merge existing threads

    unique_threads = monthly_threads[0]
    thread_names = []
    for thread in unique_threads:
        thread_names.append(thread["name"])

    for i in range(1,len(monthly_threads)):
        threads_of_the_month = monthly_threads[i]
        for thread in threads_of_the_month:
            thread_name = thread["name"]
            if thread_name in thread_names:
                r = 0
                while not(unique_threads[r]["name"] == thread_name):
                    r += 1
                unique_threads[r]["commenters_ids"] += thread["commenters_ids"]
            else:
                unique_threads.append(thread)
                thread_names.append(thread["name"])

    return unique_threads