# This script is used to generate names of subreddits of each group (random, similar, clashing)
# It goes through all subreddits and finds some above a certain number of threads

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


data_path = 'E:/bz2_files/' # where are the bz2 files?
home_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/WINTER/3-Topics in CSS/3_Project/Code/subreddit names/'
starting_year = 2016
starting_month = 1
ending_year = 2016
ending_month = 1
min_threads = 100*(ending_month - starting_month + 1)
nb_of_subr = 50
model = gensim.models.KeyedVectors.load_word2vec_format('C:/Users/mathi/Documents/DATA SCIENCE/KAGGLE/Toxic_Kaggle/GoogleNews-vectors-negative300.bin', binary=True)
random_thres = 0.025
similar_thres = 0.4
attempts_coeff = 4


# process the name of each subreddit
def preproc(name):
    # 1: remove underscores
    temp = name.replace('_','')
    # 2: remove numbers
    temp = re.sub(r'[0-9]+', '', temp)
    # 3: split on capital letters
    split = re.findall('[A-Z][^A-Z]*', temp)
    if split == []:
        split = [temp]
    # 4: part-of-speech tagging to identify proper nouns
    tagged_sent = nltk.pos_tag(split)
    vectors = []
    for i in range(len(tagged_sent)):
        if tagged_sent[i][1] == 'NNP':
            try:
                embedding = model[tagged_sent[i][0]]
                vectors.append(embedding)
            except KeyError:
                continue
        else:
            try:
                embedding = model[tagged_sent[i][0].lower()]
                vectors.append(embedding)
            except KeyError:
                continue            
    if vectors == []:
        return 'Subreddit name not recognized by the word2vec model'
    else:
        return np.mean(np.array(vectors), axis=0)

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
        while ((subreddits[keys[i]] < min_threads) or (i in indices)) and (attempts <= 4*len(keys)):
            i = np.random.randint(len(keys))
            attempts += 1
        if subreddits[keys[i]] >= min_threads:
            indices.append(i)
            names.append(keys[i])

    return names

# compute the cosine similarity between a group of subreddits and a given subreddit under study 
# returns a dictionary whose keys are subreddit names and values cosine similarities
def group_similarity(pair_element, names):

    ref = prepoc(pair_element)
    similarities = {}

    for name in names:
        embedding = preproc(name)
        if type(embedding) != str:
            similarities[name] = cosine_similarity(ref.reshape((1,300)), embedding.reshape((1,300)))[0][0]
        else:
            similarities[name] = embedding

    return similarities

# computes cosine similarity of all pairs of subreddits
def similarities(names, home_path):

    os.chdir(home_path)

    similarities = {}
    random_pairs = []
    similar_pairs = []

    for name in names:
        embedding = preproc(name)
        if type(embedding) != str:
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
                        if abs(cos) >= similar_thres:
                            if not([other_name, name] in similar_pairs):
                                similar_pairs.append([name,other_name])
                    else:
                        similarities[name][other_name] = other_embedding
        else:
            similarities[name] = embedding

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
            file.write(pair[0]+','+pair[1]+'\n')
    print('We finished writing similar pairs')    


if __name__ == '__main__':

    subreddits = screen_threads(data_path, starting_year, starting_month, ending_year, ending_month)
    print('In this period, we have found {} subreddits'.format(len(list(subreddits.keys()))))

    names = random_subs(subreddits, min_threads, nb_of_subr)
    print('We have selected the following {} subreddits matching your criteria: {}'.format(len(names),names))

    similarities(names, home_path)

