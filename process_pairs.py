# Utility functions for subreddit names

import numpy as np 
import f
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