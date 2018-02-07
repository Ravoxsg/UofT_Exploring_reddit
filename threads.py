import numpy as np 
import os
import csv
import ast 
from tqdm import tqdm
import yaml


# PARAMETERS
data_path = 'data/'
starting_year = 2006
starting_month = 1
ending_year = 2006
ending_month = 3
subreddit = "nsfw" 

all_threads = [] # list containing all threads of a given subreddit, each thread is a dictionary 
# each thread dictionary contains the following entries:
# name, author, num_comments, commenters_ids
thread_names = []

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
                try:
                    thread_dico = yaml.load(s) # transforms the string into a dictionary - not sure it always works !
                    if thread_dico != None:
                        if thread_dico["subreddit"] == subreddit:
                            new_thread = {}
                            # grabbing the fields that interest us
                            new_thread["name"] = thread_dico["name"]
                            thread_names.append(thread_dico["name"])
                            new_thread["author"] = thread_dico["author"]
                            new_thread["num_comments"] = thread_dico["num_comments"]
                            new_thread["commenters_ids"] = []
                            all_threads.append(new_thread)
                except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                    continue

print("Total number of threads: {}".format(len(all_threads)))

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
                try:
                    comment_dico = yaml.load(sub_data[i])
                    if comment_dico != None:
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
                except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                    continue

print("New total number of threads: {}".format(len(all_threads)))
print(all_threads)
