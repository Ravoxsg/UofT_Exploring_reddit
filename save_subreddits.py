# Based on generate_random_pairs.py
# Substitute when subreddits extraction went well, but it then crashed

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
import re
import nltk
import operator

from nlp_utils import preproc


data_path = 'E:/bz2_files/' # where are the bz2 files?
home_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/WINTER/3-Topics in CSS/3_Project/Exploring_Reddit/subreddit names/'
starting_year = 2016
starting_month = 1
ending_year = 2016
ending_month = 12
min_threads = 150*(ending_month - starting_month + 1)
nb_of_subr = 2500
random_thres = 0.02 # lower than that means random
similar_thres = 0.5 # higher than that means similar
attempts_coeff = 5
clashing_pairs = ["prolife","prochoice","The_Donald","HillaryForAmerica","Feminism","TheRedPill","climatechange","climateskeptics"]
#clashing_pairs = ["reddit.com","nsfw"]

# randomly select distinct subreddits that have enough threads
def random_subs(subreddits, min_threads, nb_of_subr):

    keys = list(subreddits.keys())

    if (nb_of_subr >= len(keys)):
        print("WARNING: you are trying to grab more subreddits than there actually are")

    indices = []
    names = []

    attempts = 0
    while (attempts <= attempts_coeff*len(keys)) and (len(indices) < nb_of_subr):
        #print(attempts)
        i = np.random.randint(len(keys))
        attempts += 1
        while ((subreddits[keys[i]] < min_threads) or (i in indices)) and (attempts <= attempts_coeff*len(keys)):
            i = np.random.randint(len(keys))
            attempts += 1
        if (subreddits[keys[i]] >= min_threads) and not(i in indices):
            indices.append(i)
            names.append(keys[i])

    return names

# find similar and random subreddits associated to a given subreddit (member of a clashing pair for instance)
def group_similarity(subreddits, pair_element, names):

    os.chdir(home_path+"clashing_pairs_specific/")
    ref = preproc(pair_element)

    if type(ref) != str:

        similar = []
        random = []

        for name in names:
            if name != pair_element:
                embedding = preproc(name)
                if type(embedding) != str:
                    cos = cosine_similarity(ref.reshape((1,300)), embedding.reshape((1,300)))[0][0]
                    if abs(cos) >= similar_thres:
                        similar.append((name, cos))
                    if abs(cos) <= random_thres:
                        random.append((name, cos))

        similar = sorted(similar, key=lambda x: x[1], reverse=True)
        random = sorted(random, key=lambda x: x[1], reverse=True)
        
        with open('{}_similarities.csv'.format(pair_element), 'w') as file:
            try:
                file.write(pair_element+','+str(subreddits[pair_element])+'\n')
                file.write('similar'+'\n')
                for i in range(len(similar)):
                    file.write(str(similar[i][0])+','+str(similar[i][1])+','+str(subreddits[similar[i][0]])+'\n')
                file.write('random'+'\n')
                for i in range(len(random)):
                    file.write(str(random[i][0])+','+str(random[i][1])+','+str(subreddits[random[i][0]])+'\n')
            except KeyError:
                return "Sorry, one of the subreddits is unknown to us"

        print("We finished finding subreddits associated with: {}".format(pair_element))

    else:

        print("Sorry, {} was not recognized by the word embeddings model".format(pair_element))

# computes cosine similarity of all pairs of subreddits
def similarities(names, home_path):

    os.chdir(home_path)

    similarities = {}
    random_pairs = []
    similar_pairs = []

    n_recognized = 0
    n_random = 0
    n_similar = 0

    for name in names:
        embedding = preproc(name)
        if type(embedding) != str:
            n_recognized += 1
            similarities[name] = {}
            for other_name in names:
                if other_name != name:
                    other_embedding = preproc(other_name)
                    if type(other_embedding) != str:
                        cos = cosine_similarity(embedding.reshape((1,300)), other_embedding.reshape((1,300)))[0][0]
                        similarities[name][other_name] = cos
                        if abs(cos) <= random_thres:
                            if not([other_name, name] in random_pairs):
                                random_pairs.append([name,other_name])
                                n_random += 1
                        if abs(cos) >= similar_thres:
                            if not([other_name, name] in similar_pairs):
                                similar_pairs.append(([name,other_name], cos))
                                n_similar += 1
                    else:
                        similarities[name][other_name] = other_embedding
        else:
            similarities[name] = embedding

    similar_pairs = sorted(similar_pairs, key=lambda x: x[1], reverse=True)

    # write similarities dico
    with open('similarities_{}_{}_to_{}_{}_{}_subs_{}_per_month.csv'.format(starting_year, starting_month, ending_year, ending_month, nb_of_subr, int(min_threads/(ending_month-starting_month+1))), 'w') as file:
        file.write("subreddit"+','+"subreddit"+"\n")
        for key in similarities.keys():
            file.write(key+"\n")
            if type(similarities[key]) != str:
                for name in similarities[key].keys():
                    file.write(","+name+','+str(similarities[key][name])+"\n")
    print('We finished writing similarities between all subreddits')

    # write random pairs
    with open('random_pairs_{}_{}_to_{}_{}_{}_subs_{}_per_month.csv'.format(starting_year, starting_month, ending_year, ending_month, nb_of_subr, int(min_threads/(ending_month-starting_month+1))), 'w') as file:
         file.write("subreddit 1"+','+"subreddit 2"+"\n")
         for pair in random_pairs:
            file.write(pair[0]+','+pair[1]+'\n')
    print('We finished writing random pairs')

    # write similar pairs
    with open('similar_pairs_{}_{}_to_{}_{}_{}_subs_{}_per_month.csv'.format(starting_year, starting_month, ending_year, ending_month, nb_of_subr, int(min_threads/(ending_month-starting_month+1))), 'w') as file:
         file.write("subreddit 1"+','+"subreddit 2"+"\n")
         for pair in similar_pairs:
            file.write(pair[0][0]+','+pair[0][1]+'\n')
    print('We finished writing similar pairs')

    return n_recognized/len(names), n_random, n_similar    


if __name__ == '__main__':

    subreddits = {}
    with open(home_path+'subreddits_sizes_2016_1_to_2016_12_150_per_month.csv', 'r') as file:
        rows = csv.reader(file)
        for row in rows:
            subreddits[row[0]] = int(row[1])
    #print(subreddits)

    names = random_subs(subreddits, min_threads, nb_of_subr)
    print('We have selected the following {} subreddits matching your criteria: {}'.format(len(names),names))

    for clashing_element in clashing_pairs:
        group_similarity(subreddits, clashing_element, names)

    reco, random, similar = similarities(names, home_path)
    print('Fraction of subreddit names recognized by the word embeddings model: {}'.format(reco))
    print('Number of random pairs found: {}'.format(random))
    print('Number of similar pairs found: {}'.format(similar))

