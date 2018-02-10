import numpy as np 
import os
import csv
import ast 
from tqdm import tqdm
import yaml
import time


# PARAMETERS
data_path = 'E:/Reddit/extracted_files'
starting_year = 2006
starting_month = 1
ending_year = 2006
ending_month = 3
subreddit = "reddit.com" 


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

def initialize_threads(data_path, starting_year, starting_month, ending_year, ending_month, subreddit):

    all_threads = [] # list containing all threads of a given subreddit, each thread is a dictionary 
    # each thread dictionary contains the following entries:
    # name, author, num_comments, commenters_ids
    thread_names = []
    failed_conversions = 0
    times = []

    os.chdir(data_path)

    # go through the post submissions first
    for filename in tqdm(os.listdir('.')):
        date = filename[3:].split('-')
        year = int(date[0])
        month = int(date[1])
        # taking files relevant to us
        if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
            if filename.startswith('RS_'):
                sub_data = (open(filename, 'r').read()).split('\n') # reading the text data
                print('Number of threads this month: {}'.format(len(sub_data)))
                for i in range(len(sub_data)):
                    s = sub_data[i] # this is a string
                    time1 = time.time()
                    thread_dico = string_to_dic(s)
                    time2 = time.time()
                    times.append(time2-time1)
                    try:
                        if (thread_dico != None) & (thread_dico != {}):
                            if thread_dico["subreddit"] == subreddit:
                                new_thread = {}
                                # grabbing the fields that interest us
                                new_thread["name"] = thread_dico["name"]
                                thread_names.append(thread_dico["name"])
                                new_thread["author"] = thread_dico["author"]
                                new_thread["num_comments"] = thread_dico["num_comments"]
                                new_thread["commenters_ids"] = []
                                all_threads.append(new_thread)
                    except KeyError:
                        failed_conversions += 1
                        continue

    return all_threads, thread_names, times, failed_conversions

def map_comments(all_threads, thread_names, starting_year, starting_month, ending_year, ending_month):

    # now go though the comments files
    for filename in tqdm(os.listdir('.')):
        date = filename[3:].split('-')
        year = int(date[0])
        month = int(date[1])
        if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
            if filename.startswith('RC_'):
                sub_data = (open(filename, 'r').read()).split('\n')
                print('Number of comments this month: {}'.format(len(sub_data)))
                for i in range(len(sub_data)):
                    comment_dico = string_to_dic(sub_data[i])
                    if comment_dico != None:
                        try:
                            if comment_dico["subreddit"] == subreddit:
                                if comment_dico["author"] != '[deleted]': # some comment authors deleted their account
                                    # perhaps this comment concerns a thread that was created during the studied period
                                    if comment_dico["link_id"] in thread_names:
                                        r = 0
                                        # in this case, we just iterate in our threads list until we find it
                                        while all_threads[r]["name"] != comment_dico["link_id"]:
                                            r += 1
                                        all_threads[r]["commenters_ids"].append(comment_dico["author"])
                                    # the author option is that the comment refers to an older thread - in that case, we make a new value on our threads list
                                    else:
                                        new_thread = {}
                                        new_thread["name"] = comment_dico["parent_id"]
                                        thread_names.append(comment_dico["parent_id"])
                                        new_thread["author"] = "" # we don't know the author of this thread
                                        new_thread["num_comments"] = -1 # we don't know the number of comments in this thread, so put a dummy value
                                        new_thread["commenters_ids"] = [comment_dico["author"]]
                                        all_threads.append(new_thread)
                        except KeyError:
                            continue

    return all_threads


if __name__ == '__main__':

    all_threads, thread_names, times, failed_conversions = initialize_threads(data_path, starting_year, starting_month, ending_year, ending_month, subreddit)

    print("Total number of threads: {}".format(len(all_threads)))
    print("Success rate of dictionary conversion: {}".format((len(all_threads)-failed_conversions)/len(all_threads)))
    print("Average time to convert into a dico: {} ms".format(1000*np.mean(np.array(times))))

    threads = map_comments(all_threads, thread_names, starting_year, starting_month, ending_year, ending_month)

    print("New total number of threads: {}".format(len(threads)))
    print(threads)

