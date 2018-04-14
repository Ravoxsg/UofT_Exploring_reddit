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

#from nlp_utils import preproc
#from generate_random_pair import random_thres


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

def sport_pairs():

    team_cities = {"leafs": "T", "Torontobluejays": "T", "torontoraptors": "T",
    "Patriots": "B", "BostonBruins": "B", "redsox": "B", "bostonceltics": "B",
    "NYGiants": "NY", "rangers": "NY", "NYYankees": "NY", "NYKnicks": "NY",
    "hawks": "C", "CHICubs": "C", "chicagobulls": "C",
    "Chargers": "LA", "losangeleskings": "LA", "Dodgers": "LA", "lakers":"LA",
    "DenverBroncos": "D", "ColoradoAvalanche": "D", "ColoradoRockies": "D", "denvernuggets": "D"}

    team_sports = {"leafs": "hockey", "Torontobluejays": "baseball", "torontoraptors": "basketball",
    "Patriots": "footbal", "BostonBruins": "hockey", "redsox": "baseball", "bostonceltics": "basketball",
    "NYGiants": "football", "rangers": "hockey", "NYYankees": "baseball", "NYKnicks": "basketball",
    "hawks": "hockey", "CHICubs": "baseball", "chicagobulls": "basketball",
    "Chargers": "football", "losangeleskings": "hockey", "Dodgers": "baseball", "lakers":"basketball",
    "DenverBroncos": "football", "ColoradoAvalanche": "hockey", "ColoradoRockies": "baseball", "denvernuggets": "basketball"}

    similar_pairs = []
    clashing_pairs = []
    random_pairs = []

    for team_a in list(team_cities.keys()):
        for team_b in list(team_cities.keys()):
            if team_a != team_b:
                if team_cities[team_a] == team_cities[team_b]:
                    similar_pairs.append([team_a, team_b])
                elif team_sports[team_a] == team_sports[team_b]:
                    clashing_pairs.append([team_a, team_b])
                else:
                    random_pairs.append([team_a, team_b])

    all_pairs = {"conflict": clashing_pairs, "similar": similar_pairs, "random": random_pairs}

    print(clashing_pairs)
    print(similar_pairs)
    print(random_pairs)

    with open('sport_pairs.pickle', 'wb') as handle:
        pickle.dump(all_pairs, handle)


if __name__ == '__main__':

    sport_pairs()