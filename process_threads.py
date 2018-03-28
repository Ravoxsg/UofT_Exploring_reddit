# Utility functions 

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
from sklearn.metrics.pairwise import cosine_similarity as cos

import pdb

from nlp_utils import preproc
from generate_random_pair import random_thres

# merge threads from the same subreddit over different months
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

# stores each control group 
def pairs_index():

    clashing_elements = ["prolife", "prochoice", "The_Donald", "HillaryForAmerica", "Feminism", "TheRedPill",
    "climatechange", "climateskeptics"]

    clashing_pairs = [["prolife", "prochoice"], ["The_Donald", "HillaryForAmerica"],
    ["Feminism", "TheRedPill"], ["climatechange","climateskeptics"]]

    non_clashing_elements = ["prohealth", "2016_elections", "Anarchism", "PurplePillDebate", "climate", "fastfood",
    "FoodFans","Calligraphy","bookbinding"]

    similar_pairs = [["prolife","prohealth"], ["prolife","prohealth"],
    ["The_Donald", "2016_elections"], ["HillaryForAmerica", "2016_elections"],
    ["Feminism", "Anarchism"], ["TheRedPill", "PurplePillDebate"],
    ["climatechange","climate"], ["climateskeptics", "climate"]]

    random_pairs = []
    n = len(clashing_elements)
    for i in range(n):
        j = np.random.randint(n)
        while i == j:
            j = np.random.randint(n)
        random_pairs.append([clashing_elements[i], similar_pairs[j][1]])

    control_similar_pairs = [["fastfood","FoodFans"], ["Calligraphy", "bookbinding"]]

    control_random_pairs = []
    m = len(non_clashing_elements)
    for i in range(m):
        for j in range(i+1,m):
            if (type(preproc(non_clashing_elements[i])) != str) and (type(preproc(non_clashing_elements[j])) != str):
                if abs(cos(preproc(non_clashing_elements[i]).reshape((1,300)), preproc(non_clashing_elements[j]).reshape((1,300)))[0][0]) < random_thres:
                    control_random_pairs.append([non_clashing_elements[i], non_clashing_elements[j]])

    all_pairs = {"conflict": clashing_pairs, "similar": similar_pairs,
    "random": random_pairs, "control_similar": control_similar_pairs, "control_random": control_similar_pairs}

    print(all_pairs)

    with open('pairs_index.pickle', 'wb') as handle:
        pickle.dump(all_pairs, handle)


if __name__ == '__main__':

    pairs_index()
