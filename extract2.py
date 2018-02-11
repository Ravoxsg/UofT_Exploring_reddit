# -*- coding: utf-8 -*-
"""
Created on Fri Jan 05 16:29:01 2018

@author: Jocelyn
"""

import os
import json
import sys
import utils
import pandas as pd
from pandas.io.json import json_normalize
import bz2
import gc

mainDir = os.path.dirname(os.path.realpath('__file__'))

extractedData = []

targetSubreddits = set(map(lambda x : x.strip("/r/").lower(),utils.loadJson(os.path.join(mainDir,"listeSubreddits.json")).keys()))

listRC = os.listdir(os.path.join(mainDir,"bz2","RC_2017"))
listRS = os.listdir(os.path.join(mainDir,"bz2","RS_2017"))

columnsToKeepRS = ["author","created_utc","domain","gilded","id","media","num_comments","permalink","retrieved_on","score","subreddit","subreddit_id","title","url","selftext","secure_media","stickied"]

def extractSubredditsRC(fichier,targetSubreddits):
    statinfo = os.stat(os.path.join(mainDir,"bz2","RC_2017",fichier))
    compteur = utils.Compt(6*statinfo.st_size)
    
    bz_file = bz2.BZ2File(os.path.join(mainDir,"bz2","RC_2017",fichier))
    #line_list = bz_file.readlines()
    liste = []
    metaliste = []
    c = 0
    for line in bz_file: 
        compteur.updateAndPrint2(sys.getsizeof(line))          
        subreddit = line.split('"subreddit":')[1].split(",")[0].strip('"')
        if subreddit.lower() in targetSubreddits:
            liste.append(json_normalize(json.loads(line)))
            c += 1
        if c == 10000:
            print("/!\ small concat!")
            metaliste.append(pd.concat(liste))
            liste = []
            gc.collect()
            c = 0
    if liste:
        metaliste.append(pd.concat(liste))
    print("/!\ closing")
    bz_file.close()
    print("/!\ cleaning")
    gc.collect()
    print("/!\ concat")
    df = pd.concat(metaliste)
    return df

def extractSubredditsRS(fichier,targetSubreddits):
    statinfo = os.stat(os.path.join(mainDir,"bz2","RS_2017",fichier))
    compteur = utils.Compt(6*statinfo.st_size)
    
    bz_file = bz2.BZ2File(os.path.join(mainDir,"bz2","RS_2017",fichier))
    #line_list = bz_file.readlines()
    liste = []
    metaliste = []
    c = 0
    for line in bz_file: 
        compteur.updateAndPrint2(sys.getsizeof(line))
        if '"subreddit":' in line:
            subreddit = line.split('"subreddit":')[1].split(",")[0].strip('"')
            if subreddit.lower() in targetSubreddits:
                tmp = json_normalize(json.loads(line))
                for col in columnsToKeepRS:
                    if col not in tmp:
                        tmp[col] = None
                liste.append(tmp[columnsToKeepRS])
                c += 1
            if c == 10000:
                print("/!\ small concat!")
                metaliste.append(pd.concat(liste))
                liste = []
                gc.collect()
                c = 0
    if liste:
        metaliste.append(pd.concat(liste))
    print("/!\ closing")
    bz_file.close()
    print("/!\ cleaning")
    gc.collect()
    print("/!\ concat")
    df = pd.concat(metaliste)
    return df

for RC in listRC:
    if RC.endswith(".bz2"):
        if not os.path.exists(os.path.join(mainDir,"graph",RC.split(".")[0]+".csv")):
            print("Doing : "+os.path.join(mainDir,"bz2","RC_2017",RC))
            df = extractSubredditsRC(RC,targetSubreddits)
            df.to_csv(os.path.join(mainDir,"graph",RC.split(".")[0]+".csv"),encoding="utf8")
        else:
            print(os.path.join(mainDir,"bz2","RC_2017",RC) + " already exists.")
        
for RS in listRS:
    if not os.path.exists(os.path.join(mainDir,"graph",RS.split(".")[0]+".csv")):
        print("Doing : "+os.path.join(mainDir,"bz2","RS_2017",RS))
        df = extractSubredditsRS(RS,targetSubreddits)
        df.to_csv(os.path.join(mainDir,"graph",RS.split(".")[0]+".csv"),encoding="utf8")
    else:
        print(os.path.join(mainDir,"bz2","RS_2017",RS) + " already exists.")