# Gives a certain number of subreddits all distinct and containing a minimum number of threads

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

data_path = 'E:/bz2_files/' # where are the bz2 files?
starting_year = 2016
starting_month = 1
ending_year = 2016
ending_month = 10
min_threads = 50
nb_of_subr = 6

def screen_threads(data_path, starting_year, starting_month, ending_year, ending_month):

    os.chdir(data_path)

    subreddits = {}

    # go through the post submissions first
    for filename in os.listdir('.'):
        if filename.startswith('RS'): # was getting issues since it would pick up files that were not RS_, or RC_
            date = filename[3:-4].split('-')
            year = int(date[0])
            month = int(date[1])
            # taking files relevant to us
            if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
                if filename.startswith('RS_'):
                    bz_file = bz2.BZ2File(filename)
                    for line in tqdm(bz_file):
                        try:
                            thread_dico = json.loads(line.decode("utf-8"))
                            if (thread_dico != None) & (thread_dico != {}):
                                if thread_dico["subreddit"] in subreddits.keys():
                                    subreddits[thread_dico["subreddit"]] += 1
                                else:
                                    subreddits[thread_dico["subreddit"]] = 1
                        except KeyError:
                            continue
    return subreddits

def random_pair(subreddits):

    keys = list(subreddits.keys())

    indices = []
    names = []

    for r in range(nb_of_subr):
        i = np.random.randint(len(keys))
        while not(subreddits[keys[i]] >= min_threads) or (i in indices):
            i = np.random.randint(len(keys))
        indices.append(i)
        names.append(keys[i])

    return names

if __name__ == '__main__':

    subreddits = screen_threads(data_path, starting_year, starting_month, ending_year, ending_month)
    indices = random_pair(subreddits)
    print(indices)