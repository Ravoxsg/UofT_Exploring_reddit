# Gives a certain number of subreddits all distinct and containing a minimum number of threads
# Also passes these subreddits names to a word2vec embeddings to get their cosine similarity with a given subreddit name. 

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
import gensim
from sklearn.metrics.pairwise import cosine_similarity

data_path = 'E:/bz2_files/' # where are the bz2 files?
starting_year = 2006
starting_month = 1
ending_year = 2006
ending_month = 3
min_threads = 5
nb_of_subr = 20
model = gensim.models.KeyedVectors.load_word2vec_format('C:/Users/mathi/Documents/DATA SCIENCE/KAGGLE/Toxic_Kaggle/GoogleNews-vectors-negative300.bin', binary=True)

# grab all subreddits in the given period
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

# randomly select distinct subreddits that have enough threads
def random_pair(subreddits):

    if (nb_of_subr >= len(subreddits)):
        print("WARNING: you are trying to grab more subreddits than there actually are")

    keys = list(subreddits.keys())

    indices = []
    names = []

    attempts = 0
    while (attempts <= 3*len(subreddits)) and (len(indices) < nb_of_subr):
        i = np.random.randint(len(keys))
        attempts += 1
        while not(subreddits[keys[i]] >= min_threads) or (i in indices):
            i = np.random.randint(len(keys))
            attempts += 1
        indices.append(i)
        names.append(keys[i])

    return names

# compute the cosine similarity between these subreddits names and a given subreddit under study 
# returns a dictionary whose keys are subreddit names and values cosine similarities
def similarity(pair_element, names):


    ref = model[pair_element]
    similarities = {}

    for name in names:
        try:
            embedding = model[name]
            similarities[name] = cosine_similarity(ref.reshape((1,300)), embedding.reshape((1,300)))[0][0]
        except KeyError:
            similarities[name] = 'Subreddit name not recognized by the word2vec model'

    return similarities


if __name__ == '__main__':

    subreddits = screen_threads(data_path, starting_year, starting_month, ending_year, ending_month)
    names = random_pair(subreddits)
    print(names)
    similarities = similarity('prolife', names)
    print(similarities)
    print(cosine_similarity(model['prolife'].reshape((1,300)), model['prochoice'].reshape((1,300)))[0][0])
    print(cosine_similarity(model['democrats'].reshape((1,300)), model['republicans'].reshape((1,300)))[0][0])