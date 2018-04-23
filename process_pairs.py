# Utility functions for subreddit names

import numpy as np 
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

from nlp_utils import preproc, c2v_model
from generate_random_pair import random_thres


# stores each control group 
def pairs_index():

    clashing_elements = ["prolife", "prochoice", "The_Donald", "HillaryForAmerica", "Feminism", "TheRedPill",
    "climatechange", "climateskeptics"]

    clashing_pairs = [["prolife", "prochoice"], ["The_Donald", "HillaryForAmerica"],
    ["Feminism", "TheRedPill"], ["climatechange","climateskeptics"]]

    non_clashing_elements = ["prohealth", "2016_elections", "Anarchism", "PurplePillDebate", "climate", "fastfood",
    "FoodFans", "Calligraphy", "bookbinding", "70smusics", "80smusic"]

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

    control_similar_pairs = [["fastfood", "FoodFans"], ["Calligraphy", "bookbinding"], ["80smusic", "70smusic"]]

    control_random_pairs = []
    m = len(non_clashing_elements)
    for i in range(m):
        for j in range(i+1,m):
            if (type(preproc(non_clashing_elements[i])) != str) and (type(preproc(non_clashing_elements[j])) != str):
                if abs(cos(preproc(non_clashing_elements[i]).reshape((1,300)), preproc(non_clashing_elements[j]).reshape((1,300)))[0][0]) <= random_thres:
                    control_random_pairs.append([non_clashing_elements[i], non_clashing_elements[j]])

    all_pairs = {"conflict": clashing_pairs, "similar": similar_pairs,
    "random": random_pairs, "control_similar": control_similar_pairs, "control_random": control_random_pairs}

    print(all_pairs)

    with open('pairs_index.pickle', 'wb') as handle:
        pickle.dump(all_pairs, handle)

# stores each control group in the sport teams use case
def sport_pairs(team_cities, team_sports):

    similar_pairs = []
    clashing_pairs = []
    random_pairs = []

    for team_a in list(team_cities.keys()):
        for team_b in list(team_cities.keys()):
            if team_a != team_b:
                if team_cities[team_a] == team_cities[team_b]:
                    if not([team_b, team_a] in similar_pairs):
                        similar_pairs.append([team_a, team_b])
                elif team_sports[team_a] == team_sports[team_b]:
                    if not([team_b, team_a] in clashing_pairs):
                        clashing_pairs.append([team_a, team_b])
                else:
                    if not([team_b, team_a] in random_pairs):
                        random_pairs.append([team_a, team_b])

    all_pairs = {"conflict": clashing_pairs, "similar": similar_pairs, "random": random_pairs}

    print('Number of clashing pairs: {}'.format(len(clashing_pairs)))
    print('Number of similar pairs: {}'.format(len(similar_pairs)))
    print('Number of random pairs: {}'.format(len(random_pairs)))

    with open('sport_pairs.pickle', 'wb') as handle:
        pickle.dump(all_pairs, handle)

    return all_pairs

# average distance between two pairs in the words embeddings representation
def distance_pairs_nlp(all_pairs):

    clashing_distances = []
    for pair in all_pairs["conflict"]:
        team_a = pair[0]
        team_b = pair[1]
        if (type(preproc(team_a)) != str) and (type(preproc(team_b)) != str):
            distance = abs(cos(preproc(team_a).reshape((1,300)), preproc(team_b).reshape((1,300)))[0][0])
            clashing_distances.append(distance)

    similar_distances = []
    for pair in all_pairs["similar"]:
        team_a = pair[0]
        team_b = pair[1]
        if (type(preproc(team_a)) != str) and (type(preproc(team_b)) != str):
            distance = abs(cos(preproc(team_a).reshape((1,300)), preproc(team_b).reshape((1,300)))[0][0])
            similar_distances.append(distance)

    random_distances = []
    for pair in all_pairs["random"]:
        team_a = pair[0]
        team_b = pair[1]
        if (type(preproc(team_a)) != str) and (type(preproc(team_b)) != str):
            distance = abs(cos(preproc(team_a).reshape((1,300)), preproc(team_b).reshape((1,300)))[0][0])
            random_distances.append(distance)

    return np.mean(np.array(clashing_distances)), np.mean(np.array(similar_distances)), np.mean(np.array(random_distances))

# average distance between two pairs in the community embeddings representation
def distance_pairs_c2v(all_pairs):

    c2v_embeddings = c2v_model('../big files/community2vec_embeddings.csv')

    clashing_distances = []
    for pair in all_pairs["conflict"]:
        team_a = pair[0]
        team_b = pair[1]
        try:
            distance = abs(cos(c2v_embeddings[team_a].reshape((1,100)), c2v_embeddings[team_b].reshape((1,100)))[0][0])
            clashing_distances.append(distance)
        except KeyError:
            continue

    similar_distances = []
    for pair in all_pairs["similar"]:
        team_a = pair[0]
        team_b = pair[1]
        try:
            distance = abs(cos(c2v_embeddings[team_a].reshape((1,100)), c2v_embeddings[team_b].reshape((1,100)))[0][0])
            similar_distances.append(distance)
        except KeyError:
            continue

    random_distances = []
    for pair in all_pairs["random"]:
        team_a = pair[0]
        team_b = pair[1]
        try:
            distance = abs(cos(c2v_embeddings[team_a].reshape((1,100)), c2v_embeddings[team_b].reshape((1,100)))[0][0])
            random_distances.append(distance)
        except KeyError:
            continue

    return np.mean(np.array(clashing_distances)), np.mean(np.array(similar_distances)), np.mean(np.array(random_distances))    


if __name__ == '__main__':

    team_cities = {"leafs": "T", "Torontobluejays": "T", "torontoraptors": "T",
    "Patriots": "B", "BostonBruins": "B", "redsox": "B", "bostonceltics": "B",
    "NYGiants": "NY", "rangers": "NY", "NYYankees": "NY", "NYKnicks": "NY",
    "hawks": "C", "CHICubs": "C", "chicagobulls": "C",
    "Chargers": "LA", "losangeleskings": "LA", "Dodgers": "LA", "lakers":"LA",
    "DenverBroncos": "D", "ColoradoAvalanche": "D", "ColoradoRockies": "D", "denvernuggets": "D"}

    team_sports = {"leafs": "hockey", "Torontobluejays": "baseball", "torontoraptors": "basketball",
    "Patriots": "football", "BostonBruins": "hockey", "redsox": "baseball", "bostonceltics": "basketball",
    "NYGiants": "football", "rangers": "hockey", "NYYankees": "baseball", "NYKnicks": "basketball",
    "hawks": "hockey", "CHICubs": "baseball", "chicagobulls": "basketball",
    "Chargers": "football", "losangeleskings": "hockey", "Dodgers": "baseball", "lakers":"basketball",
    "DenverBroncos": "football", "ColoradoAvalanche": "hockey", "ColoradoRockies": "baseball", "denvernuggets": "basketball"}

    all_pairs = sport_pairs(team_cities, team_sports)

    print('Distance in word embeddings')
    clashing_d_nlp, similar_d_nlp, random_d_nlp = distance_pairs_nlp(all_pairs)
    print('Average distance between clashing pairs: {}'.format(clashing_d_nlp))
    print('Average distance between similar pairs: {}'.format(similar_d_nlp))
    print('Average distance between random pairs: {}'.format(random_d_nlp))

    print('Distance in community embeddings')
    clashing_d_c2v, similar_d_c2v, random_d_c2v = distance_pairs_c2v(all_pairs)
    print('Average distance between clashing pairs: {}'.format(clashing_d_c2v))
    print('Average distance between similar pairs: {}'.format(similar_d_c2v))
    print('Average distance between random pairs: {}'.format(random_d_c2v))