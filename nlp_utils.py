# Functions useful to process subreddit names

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

from math import log


# PARAMETERS
# path for the word2vec model trained on Google News
model = gensim.models.KeyedVectors.load_word2vec_format('C:/Users/mathi/Documents/DATA SCIENCE/KAGGLE/Toxic_Kaggle/GoogleNews-vectors-negative300.bin', binary=True)
# path for the community2vec model
c2v_matrix_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/2_WINTER/3-Topics in CSS/3_Project/big files/community2vec_embeddings.csv'
# word types frequency list
words = open("words_by_frequency.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)


# splits concatenated lower case words into a list of these words
def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))

# processes the name of each subreddit
def preproc(name):
    # 1: remove underscores
    temp = name.replace('_','')
    # 2: remove numbers
    temp = re.sub(r'[0-9]+', '', temp)
    # 3: split on capital letters
    # treat abbreviations differently
    if temp.isupper():
        split = [temp]
    else:
        # there might not be any uppercase letter - in this case, infer spaces
        if temp.islower():
            split = infer_spaces(temp).split(" ")
        # if there are, split on them
        else:
            split = re.findall('[A-Z][^A-Z]*', temp)
    # 4: part-of-speech tagging to identify proper nouns
    try:
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
    except IndexError:
        return 'Subreddit name not recognized by the pos tagging model'

# represents the name of each subreddit via community embeddings
def c2v_model(input_path=c2v_matrix_path):

    c2v_embeddings = {}
    f = open(input_path, 'r')
    for line in tqdm(csv.DictReader(f)):
        for subreddit in line.keys():
            if subreddit in c2v_embeddings.keys():
                c2v_embeddings[subreddit].append(float(line[subreddit]))
            else:
                c2v_embeddings[subreddit] = [float(line[subreddit])]
    for subreddit in c2v_embeddings.keys():
        c2v_embeddings[subreddit] = np.array(c2v_embeddings[subreddit])

    return c2v_embeddings