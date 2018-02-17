
from igraph import *
import os
import pandas as pd 
import numpy as np
import math

import pickle
import random

# PARAMETERS
data_path = 'processed_threads' #I use a mac mate

subreddit = "obama" 

all_threads = [] # list containing all threads of a given subreddit, each thread is a dictionary 
# each thread dictionary contains the following entries:
# name, author, num_comments, commenters_ids
thread_names = []

os.chdir(data_path)

file_name="{}_threads".format(subreddit)
with open(file_name,'rb') as fp:
	all_threads=pickle.load(fp)

commenter_id_list=[]
thread_author_id_list=[]
all_user_id_list=[]

user_connections={}
user_count=0

user_info={}
hash_user_id={}

thread_count=0		#add the nodes

num_of_threads= len(all_threads)

thread_limit=20
for subthread in all_threads:
	if thread_count< thread_limit:
		thread_count+=1
		if thread_count%1000==0:
			print(thread_count," out of ",num_of_threads)

		commenters_ids=subthread["commenters_ids"]
		
		author=subthread["author"]

		if author not in thread_author_id_list:
			thread_author_id_list.append(author)
			if author not in all_user_id_list: #is the author in the list
				all_user_id_list.append(author)
				user_info[author]={}
				user_info[author]["user_connections"]={}
				user_count+= 1 #count the author
				

		if len(commenters_ids)>0:
			for i in range(len(commenters_ids)): #go through the commenter id's and create connections with the users
				id_commenter= commenters_ids[i]
				if id_commenter in user_info[author]["user_connections"]: #if this already exists
					if id_commenter!=author: #we are not interested in the author commenting on themselves
						user_info[author]["user_connections"][id_commenter].append(('a', thread_count,i+1)) #save the type of relationship as well as the index of the commmenter
				else:
					if id_commenter!=author: 
						user_info[author]["user_connections"][id_commenter]=[('a', thread_count,i+1)] # first initialize the list, save the type of relationship as well as the index of the commmenter

		if len(commenters_ids)>0:
			for i in range(len(commenters_ids)):
				id_commenter=commenters_ids[i]


				if id_commenter not in commenter_id_list:

					commenter_id_list.append(id_commenter)#adds commenter to the list of originally existant commenters
					if id_commenter not in all_user_id_list:
						all_user_id_list.append(id_commenter)
						user_info[id_commenter]={}
						user_info[id_commenter]["user_connections"]={}
						user_count+= 1 #count the user



				if author in user_info[id_commenter]["user_connections"]: #if this already exists
					if author!=id_commenter:
						user_info[id_commenter]["user_connections"][author].append(('a', thread_count,-(i+1))) #save the type of relationship as well as the index of the commmenter
				else:
					if author!=id_commenter:
						user_info[id_commenter]["user_connections"][author]=[('a', thread_count,-(i+1))] # first initialize the list, save the type of relationship as well as the index of the commmenter

				if len(commenters_ids)>1:
					for j in range(len(commenters_ids)):
						id_commenter_j= commenters_ids[j]
						if id_commenter_j in user_info[id_commenter]["user_connections"]: #if this already exists
							if id_commenter!=id_commenter_j: #we are not interested in the author commenting on themselves
								user_info[id_commenter]["user_connections"][id_commenter_j].append(('c', thread_count,j-i)) #save the type of relationship as well as the index of the commmenter
						else:
							if id_commenter!=id_commenter_j:
								user_info[id_commenter]["user_connections"][id_commenter_j]=[('c', thread_count,j-i)] # first initialize the list, save the type of relationship as well as the index of the commmenter
		

counter=0
user_name_list=[]
for user_name_i in list(user_info.keys()):
	hash_user_id[user_name_i]=counter
	user_name_list.append(user_name_i)
	counter+=1



id_pairs=[] # list of tuples of connection id's
pair_weight=[] #list of weights for each id_pair

print("Configuring Weights...")
counter=0
for user_name_i in list(user_info.keys()):
	counter+=1
	if counter%1000==0: 
		print(counter," out of ", user_count)
	user_i_connections=user_info[user_name_i]["user_connections"] #get the connections of user i
	user_id_i=hash_user_id[user_name_i]#get the user hash id number

	for user_name_j in list(user_i_connections.keys()):
		
		homo_connection_instances=user_i_connections[user_name_j]
		user_id_j=hash_user_id[user_name_j]#get the user hash id number
		
		threads_visited=[]#number of different threads a connection has been to

		distance=[] #sum of the connections distances
		pair_score=[] #score of the strength and direction of the pair

		for k in range(len(homo_connection_instances)):

			connection_info=homo_connection_instances[k]

			connection_type=connection_info[0]#author-commenter or commenter-commenter relationship
			connection_thread=connection_info[1]#connection thread id number
			connection_distance=connection_info[2] #relative disance between two commenters

			author_weight_pheta_0=-1
			author_weight_pheta_1=1

			commenter_weight_pheta_0=1
			commenter_weight_pheta_1=1 #distance decay factor

			#num_threads_factor*author_factor*exp(-co*b)
			#weight the decay factor based on attributes
			if connection_type=='a':
				pheta_0=np.sign(connection_distance)*author_weight_pheta_0
				pheta_1=np.abs(author_weight_pheta_1)
			if connection_type=='c':
				pheta_0=np.sign(connection_distance)*commenter_weight_pheta_0
				pheta_1=np.abs(commenter_weight_pheta_1)



			#the farther the distance the lower the follow. The function also is changed by pheta_0 and pheta_1 which depend on the users title
			distance_decay_score=pheta_0*np.exp(-np.abs(pheta_1*connection_distance))
			

			#check the number of threads the conneciton pair has visited
			threads_visited.append(connection_thread)

			distance.append(connection_distance) #append distance function to disntace
			pair_score.append(distance_decay_score) #append distance_decays_score to pair_score


		unique_threads_visited=list(set(threads_visited))#get the unique threads visited
		num_unique_threads_visited=len(unique_threads_visited)

		thread_score_factor=1

		#find the number of threads visited
		distance=np.asarray(distance)


		pair_score=np.asarray(pair_score)#convert to array

		pair_score_sum=np.sum(pair_score)#sum the non abs score terms
		pair_score_abs_sum=np.sum(np.abs(pair_score)) #sum the abs score terms of each score
		final_pair_score=thread_score_factor*pair_score_abs_sum

		
		
		
		#we should add more complicated connections depending on the distance between commentators, order of comment, and the activity level of the author

		if pair_score_sum>0:
			id_pairs.append((user_id_i,user_id_j))#get the pair id pairs
			pair_weight.append(final_pair_score)

		#import pdb; pdb.set_trace()






######################	CREATE THE FLIGHT NETWORK############################

print("Creating Graph...")
social_network= Graph(directed=False)

#add the nodes
print("Adding Vertices...")
social_network.add_vertices(user_count)

#adding airport attributes (names)

print("Adding Edges...")
social_network.add_edges(id_pairs)


#take out all the unconnected nodes

print("Removing unconnected nodes...")
social_network_degree=social_network.degree(range(user_count))
delete_vid_list=[]
for vid in range(len(social_network_degree)):
	if social_network_degree[vid]==0:
		delete_vid_list.append(vid)

social_network.delete_vertices(delete_vid_list)



print("Printing graph")

social_network.vs["name"]= user_name_list#assign each of the names of each node as teh 3 letter code for the airport
#social_network.vs["label"]=social_network.vs["name"]

social_network.es["weight"]= pair_weight #add the weights
visual_style = {}
visual_style["vertex_size"] = 2
#visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
#visual_style["vertex_label"] = social_network.vs["name"]
visual_style["edge_width"] = social_network.es["weight"]
visual_style["layout"]=social_network.layout("kk")
plot(social_network, **visual_style)


#social_network= Graph(directed=directed_network_bool)







