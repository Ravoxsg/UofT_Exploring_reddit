# created by Mathieu Ravaut
# Grabs all the threads regarding a given subreddit in a given period, and saves commenters IDs

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


# PARAMETERS
data_path = 'E:/bz2_files/' # where are the bz2 files?
output_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/WINTER/3-Topics in CSS/Project/Code/threads' # where do you want to save the threads data?
starting_year = 2006
starting_month = 1
ending_year = 2006
ending_month = 3
subreddit = "reddit.com" 

# manual way to convert string into dictionary - useless now
def string_to_dic(s):
    s=s.split(",")
    thread_dico = {}
    for i in range(len(s)):
        entry = s[i].split(":")
        if len(entry)>1:
            entry[0] = entry[0].replace('"',"")
            entry[0] = entry[0].replace('{',"")
            entry[0] = entry[0].replace('}',"")
            entry[1] = entry[1].replace('"',"")
            entry[1] = entry[1].replace('{',"")
            entry[1] = entry[1].replace('}',"")
            thread_dico[entry[0]] = entry[1]
    return thread_dico

# create one dictionary per thread that appeared in that period
def initialize_threads(data_path, starting_year, starting_month, ending_year, ending_month, subreddit):

    all_threads = [] # list containing all threads of a given subreddit, each thread is a dictionary 
    all_threads_index = {}
    # each thread dictionary contains the following entries:
    # name, author, num_comments, commenters_ids
    thread_names = []
    failed_conversions = 0
    times = []
    lines = 0

    os.chdir(data_path)

    # go through the post submissions first
    for filename in os.listdir('.'): 
        if filename.startswith("RS"):
            date = filename[3:-4].split('-')
            year = int(date[0])
            month = int(date[1])
            # taking files relevant to us
            if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
                if filename.startswith('RS_'):
                    bz_file = bz2.BZ2File(filename)
                    for line in tqdm(bz_file):
                        lines += 1
                        try:
                            time1 = time.time()
                            thread_dico = json.loads(line.decode("utf-8"))
                            time2 = time.time()
                            times.append(time2-time1)
                            if (thread_dico != None) & (thread_dico != {}):
                                if thread_dico["subreddit"] == subreddit:
                                    new_thread = {}
                                    # grabbing the fields that interest us
                                    new_thread["name"] = thread_dico["name"]
                                    thread_names.append(thread_dico["name"])
                                    new_thread["author"] = thread_dico["author"]
                                    new_thread["num_comments"] = thread_dico["num_comments"]
                                    new_thread["commenters_ids"] = []
                                    all_threads_index[thread_dico["name"]] = len(all_threads)
                                    all_threads.append(new_thread)
                        except KeyError:
                            failed_conversions += 1
                            continue
    return all_threads, all_threads_index, thread_names, times, failed_conversions/lines

# map commenters ids to threads, and if thread was created before, create a new instance of thread
def map_comments(all_threads, all_threads_index, thread_names, starting_year, starting_month, ending_year, ending_month):

    new_threads = []
    times = []
    # now go through the comments files
    for filename in os.listdir('.'):
        if filename.startswith("RC"):
            date = filename[3:-4].split('-')
            year = int(date[0])
            month = int(date[1])
            if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
                if filename.startswith('RC_'):
                    bz_file = bz2.BZ2File(filename)
                    for line in tqdm(bz_file):
                        comment_dico = json.loads(line.decode("utf-8"))
                        if comment_dico != None:
                            try:
                                if comment_dico["subreddit"] == subreddit:
                                    if comment_dico["author"] != '[deleted]': # some comment authors deleted their account
                                        time1 = time.time()
                                        # perhaps this comment concerns a thread that was created during the studied period
                                        if comment_dico["link_id"] in thread_names:
                                            all_threads[all_threads_index[comment_dico["link_id"]]]["commenters_ids"].append(comment_dico["author"])
                                        # the author option is that the comment refers to an older thread - in that case, we make a new value on our threads list
                                        else:
                                            new_thread = {}
                                            new_thread["name"] = comment_dico["parent_id"]
                                            thread_names.append(comment_dico["parent_id"])
                                            new_thread["author"] = "" # we don't know the author of this thread
                                            new_thread["num_comments"] = -1 # we don't know the number of comments in this thread, so put a dummy value
                                            new_thread["commenters_ids"] = [comment_dico["author"]]
                                            new_threads.append(new_thread)
                                        time2 = time.time()
                                        times.append(time2-time1)
                            except KeyError:
                                continue
    return all_threads + new_threads, times


if __name__ == '__main__':

    all_threads, all_threads_index, thread_names, times, failed_conversions_ratio = initialize_threads(data_path, starting_year, starting_month, ending_year, ending_month, subreddit)

    print("Total number of threads: {}".format(len(all_threads)))
    print("Success rate of dictionary conversion: {}".format(1-failed_conversions_ratio))
    print("Average time to convert into a dico: {} ms".format(1000*np.mean(np.array(times))))

    threads, times = map_comments(all_threads, all_threads_index, thread_names, starting_year, starting_month, ending_year, ending_month)

    print("New total number of threads: {}".format(len(threads)))
    print("Average time to process a comment: {} ms".format(1000*np.mean(np.array(times))))    
    print(threads)
    os.chdir(output_path)
    np.save("{}_threads_{}_{}_to_{}_{}.npy".format(subreddit,starting_month,starting_year,ending_month,ending_year), threads)

