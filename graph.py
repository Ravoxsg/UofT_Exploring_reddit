
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

#load the number of threads (format it to label 2 threads)
file_name="{}_threads".format(subreddit)
with open(file_name,'rb') as fp:
	all_threads=pickle.load(fp)

all_user_id_list=[] #record all of the user id names
user_count=0 #record the user count 

user_info={} #record all of the relevant information regarding the user
hash_user_id={} # hash user id table for user_name string to user name id

thread_count=0 #counter of the number of threads iterated

num_of_threads= 5000 #the number of maximm threads
thread_limit=num_of_threads #set the limit on the number of threads


for subthread in all_threads: #for each subthread within the commumity 
	if  thread_count> thread_limit: #if thread_count is less than the thread_limit, than terminate the loop 
		break

	else: #if thread count is less than limit continue
		
		thread_count+=1 #count the thread by 1
		if thread_count%1000==0: #print the progress in threads iterated per community
			print(thread_count," out of ",num_of_threads)

		commenters_ids=subthread["commenters_ids"] #get all of the users who comment in the thread
		
		author=subthread["author"] #get the author name


		if author not in all_user_id_list: #is the author in the list of users? If not then....
			all_user_id_list.append(author)#add user to list
			user_info[author]={} #create a key for the author in the dictionary
			user_info[author]["user_connections"]={} #add user connections
			user_count+= 1 #count the author as a apart of the new user count ()
				

		#if there are users that have commented in the thread in question
		if len(commenters_ids)>0:

			#Find all of the users in the post, record their relationship with the author 
			for i in range(len(commenters_ids)): #go through the commenter id's and create connections with the users
				id_commenter= commenters_ids[i] #user of interest (we want to find who is connected to this user in this sub-thread)
				
				if id_commenter!=author: #we dont want the interacting users being the same, (avoid redundent interactiosn)
					
					if id_commenter in user_info[author]["user_connections"]: #has this user-user interaction been previously recorded 
						#we are not interested in the author commenting on themselves

						#save the type of relationship as well as the index of the commmenter. In this case the relationship between the author and the commentator is a
						#the thread_count represents the thread_id within the community
						#the i+1 represents the relative position between the author (user of interest) and the other user
						#IMPORTANT: positive distances between users mean that user_2 is commenting after the user of interest

						user_info[author]["user_connections"][id_commenter].append(('a', thread_count,i+1)) 
					
					else:
						user_info[author]["user_connections"][id_commenter]=[('a', thread_count,i+1)] # first initialize the list, save the type of relationship as well as the index of the commmenter


			#NOW we focus on the building interactions that involve commenting users being the users of interest

			for i in range(len(commenters_ids)):

				id_commenter=commenters_ids[i] #user of interest

				if id_commenter not in all_user_id_list: # has the user of interest been seen before?
					all_user_id_list.append(id_commenter) #add user of interest to list of recorded users
					
					#establish datastructure for user
					user_info[id_commenter]={} 
					user_info[id_commenter]["user_connections"]={}
					user_count+= 1 #count the user


				#connect the user of interest with the author (negative distance because user is commenting with author's post)

				if author!=id_commenter: #ensure the user is not the author to avoid interaction redundancy
					if author in user_info[id_commenter]["user_connections"]: #if this already exists
						#save the type of relationship as well as the index of the commmenter
						user_info[id_commenter]["user_connections"][author].append(('a', thread_count,-(i+1)))
					else:
						# first initialize the list, save the type of relationship as well as the index of the commmenter
						user_info[id_commenter]["user_connections"][author]=[('a', thread_count,-(i+1))] 


				#record all user/user interactions, positive distance means that user_j has commented after user_i. 
				if len(commenters_ids)>1: #if there are more than one user in the post
					for j in range(len(commenters_ids)): #iterate through all users  
						id_commenter_j= commenters_ids[j] #second user 
						if id_commenter_j in user_info[id_commenter]["user_connections"]: #if this already exists
							if id_commenter!=id_commenter_j: #we are not interested in the author commenting on themselves
								#save the type of relationship as well as the index of the commmenter
								user_info[id_commenter]["user_connections"][id_commenter_j].append(('c', thread_count,j-i)) 
						else:
							if id_commenter!=id_commenter_j:
								# first initialize the list, save the type of relationship as well as the index of the commmenter
								user_info[id_commenter]["user_connections"][id_commenter_j]=[('c', thread_count,j-i)] 
		

counter=0 #counter
user_name_list=[]
for user_name_i in list(user_info.keys()):
	hash_user_id[user_name_i]=counter
	user_name_list.append(user_name_i)
	counter+=1

def connection_attribute_collection(connections_list, attr_index): #collects all of the attributes
	attr_list= [single_connection[attr_index] for single_connection in connections_list]
	return attr_list


#calculate the distance decay between two functions

def distance_decay_function(connection_distances_list,connection_types_list,a_weight_pheta=[1,1],c_weight_pheta=[1,1]):
	distance_decay=[]
	pheta_0,pheta_1= (0,0)
	for connection_distance,connection_type in list(zip(connection_distances_list,connection_types_list)):
		#num_threads_factor*author_factor*exp(-co*b)
		#weight the decay factor based on attributes
		if connection_type=='a':
			pheta_0=np.sign(connection_distance)*a_weight_pheta[0]
			pheta_1=np.abs(a_weight_pheta[1])
		if connection_type=='c':
			pheta_0=np.sign(connection_distance)*c_weight_pheta[0]
			pheta_1=np.abs(c_weight_pheta[1])

		#the farther the distance the lower the follow. The function also is changed by pheta_0 and pheta_1 which depend on the users title
		distance_decay.append(pheta_0*np.exp(-np.abs(pheta_1*connection_distance)))

	return distance_decay

#def loyalty_function():



print("Configuring Weights...")

id_pairs=[] # list of tuples of connection id's
pair_weight=[] #list of weights for each id_pair
counter=0


for user_name_i in list(user_info.keys()):
	counter+=1
	if counter%1000==0: 
		print(counter," out of ", user_count)
	user_i_connections=user_info[user_name_i]["user_connections"] #get the connections of user i

	for user_name_j in list(user_i_connections.keys()): #iterate through connected users of user_i
		
		connection_instances=user_i_connections[user_name_j] #find the connection instances between user i and user j 
		
		
		threads_visited=[]#number of different threads a connection has been to


		#connection thread id number
		threads_visited=connection_attribute_collection(connections_list=connection_instances, attr_index=1) #sum of the connections distances
		unique_threads_visited=list(set(threads_visited))#get the unique threads visited
		thread_score_factor=1 #scale the score based on the number of unique threads visited? for now keep it as 1


		#author-commenter or commenter-commenter relationship
		connection_types=connection_attribute_collection(connections_list=connection_instances, attr_index=0) 
		
		#relative disance between two commenters
		distances=connection_attribute_collection(connections_list=connection_instances, attr_index=2) 
		
		distances_decay= distance_decay_function(connection_distances_list=distances,
												connection_types_list=connection_types,
												a_weight_pheta=[-1,1],
												c_weight_pheta=[1,1]) #score of the strength and direction of the pair



		connection_score_sum=np.sum(np.asarray(thread_score_factor*distances_decay))#sum the non abs score terms
		connection_score_abs_sum=np.sum(np.abs(np.asarray(thread_score_factor*distances_decay))) #sum the abs score terms of each score

		weight_score= connection_score_abs_sum
		
		
		#we should add more complicated connections depending on the distance between commentators, order of comment, and the activity level of the author

		user_id_i=hash_user_id[user_name_i]#get the user hash id number
		user_id_j=hash_user_id[user_name_j]#get the user hash id number

		if connection_score_sum>0:
			id_pairs.append((user_id_i,user_id_j))#get the pair id pairs
			pair_weight.append(weight_score)

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







