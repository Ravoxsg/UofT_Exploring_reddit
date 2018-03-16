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
home_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/WINTER/3-Topics in CSS/3_Project/Code'
starting_year = 2016
starting_month = 1
ending_year = 2016
ending_month = 3
min_threads = 50
nb_of_subr = 100
model = gensim.models.KeyedVectors.load_word2vec_format('C:/Users/mathi/Documents/DATA SCIENCE/KAGGLE/Toxic_Kaggle/GoogleNews-vectors-negative300.bin', binary=True)
random_thres = 0.025
similar_thres = 0.4


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
def random_subs(subreddits, min_threads, nb_of_subr):

    if (nb_of_subr >= len(subreddits)):
        print("WARNING: you are trying to grab more subreddits than there actually are")

    keys = list(subreddits.keys())

    indices = []
    names = []

    attempts = 0
    while (attempts <= 5*len(subreddits)) and (len(indices) < nb_of_subr):
        i = np.random.randint(len(keys))
        attempts += 1
        while not(subreddits[keys[i]] >= min_threads) or (i in indices):
            i = np.random.randint(len(keys))
            attempts += 1
        indices.append(i)
        names.append(keys[i])

    return names

# compute the cosine similarity between a group of subreddits and a given subreddit under study 
# returns a dictionary whose keys are subreddit names and values cosine similarities
def group_similarity(pair_element, names):


    ref = model[pair_element]
    similarities = {}

    for name in names:
        try:
            embedding = model[name]
            similarities[name] = cosine_similarity(ref.reshape((1,300)), embedding.reshape((1,300)))[0][0]
        except KeyError:
            similarities[name] = 'Subreddit name not recognized by the word2vec model'

    return similarities

# computes cosine similarity of all pairs of subreddits
def similarities(names, home_path):

    os.chdir(home_path)

    similarities = {}
    random_pairs = []
    similar_pairs = []

    for name in names:
        try:
            embedding = model[name]
            similarities[name] = {}
            for other_name in names:
                if other_name != name:
                    try:
                        other_embedding = model[other_name]
                        cos = cosine_similarity(embedding.reshape((1,300)), other_embedding.reshape((1,300)))[0][0]
                        similarities[name][other_name] = cos
                        if abs(cos) <= random_thres:
                            random_pairs.append([name,other_name])
                        if abs(cos) >= similar_thres:
                            similar_pairs.append([name,other_name])
                    except KeyError:
                        similarities[name][other_name] = 'Subreddit name not recognized by the word2vec model' 
        except KeyError:
            similarities[name] = 'Subreddit name not recognized by the word2vec model'

    # write similarities dico
    with open('similarities.csv', 'w') as file:
        file.write("subreddit"+','+"subreddit"+"\n")
        for key in similarities.keys():
            file.write(key+"\n")
            if type(similarities[key]) != str:
                for name in similarities[key].keys():
                    file.write(","+name+','+str(similarities[key][name])+"\n")

    # write random pairs
    with open('random_pairs.csv', 'w') as file:
         file.write("subreddit 1"+','+"subreddit 2"+"\n")
         for pair in random_pairs:
            file.write(pair[0]+','+pair[1]+'\n')

    # write similar pairs
    with open('similar_pairs.csv', 'w') as file:
         file.write("subreddit 1"+','+"subreddit 2"+"\n")
         for pair in similar_pairs:
            file.write(pair[0]+','+pair[1]+'\n')    


if __name__ == '__main__':

    subreddits = screen_threads(data_path, starting_year, starting_month, ending_year, ending_month)
    names = random_subs(subreddits, min_threads, nb_of_subr)
    print(names)
    similarities(names, home_path)
    test_cosine = group_similarity('prolife', names)
    print(test_cosine)
