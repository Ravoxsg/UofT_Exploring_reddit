
from igraph import *
import pandas as pd 
import numpy as np
import math
import random
from process_threads import merge_threads
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
import pdb




class Community():
	def __init__(self,starting_year, 
				starting_month, 
				ending_year, 
				ending_month,
				subreddit,
				all_threads=None):


		if all_threads is None:
			self.all_threads=merge_threads(subreddit, starting_year, starting_month, ending_year, ending_month)
		else: 
			self.all_threads=all_threads
		self.all_user_id_list=[] #record all of the user id names
		self.user_count=0 #record the user count 

		self.user_info={} #record all of the relevant information regarding the user
		self.hash_user_id={} # hash user id table for user_name string to user name id

		self.thread_count=0 #counter of the number of threads iterated

		self.num_of_threads= len(self.all_threads) #the number of maximm threads
		self.thread_limit=self.num_of_threads #set the limit on the number of threads


		self.inter_group_users_id=[]
		self.inter_group_users_name=[]
		self.inter_group_users_loyalty=[]
		self.inter_group_users_community=[] #1 for current commmunity, 0 for other community
		self.users_interaction_status=[]#tracks the interactions status of each user based on their id


		print(subreddit)
		self.get_user_info()
		self.get_hash_user_id()
		print("Number of Users: ",self.user_count)
		print(subreddit)
		self.get_connection_weights()
		self.assign_community_status()
		self.assign_interaction_status()

	def get_user_info(self,verbose=True):

		print("getting user info")

		for subthread in self.all_threads: #for each subthread within the commumity 
			if  self.thread_count> self.thread_limit: #if thread_count is less than the thread_limit, than terminate the loop 
				break

			else: #if thread count is less than limit continue
				
				self.thread_count+=1 #count the thread by 1
				if self.thread_count%100==0 and verbose: #print the progress in threads iterated per community
					print(self.thread_count," threads processed out of ",self.num_of_threads)

				commenters_ids=subthread["commenters_ids"] #get all of the users who comment in the thread
				
				author=subthread["author"] #get the author name


				if author not in self.all_user_id_list: #is the author in the list of users? If not then....
					self.all_user_id_list.append(author)#add user to list
					self.user_info[author]={} #create a key for the author in the dictionary
					self.user_info[author]["user_connections"]={} #add user connections
					self.user_info[author]['community']=1
					self.user_info[author]['interaction_status']=0
					self.user_count+= 1 #count the author as a apart of the new user count ()
						

				#if there are users that have commented in the thread in question
				if len(commenters_ids)>0:

					#Find all of the users in the post, record their relationship with the author 
					for i in range(len(commenters_ids)): #go through the commenter id's and create connections with the users
						id_commenter= commenters_ids[i] #user of interest (we want to find who is connected to this user in this sub-thread)
						
						if id_commenter!=author: #we dont want the interacting users being the same, (avoid redundent interactiosn)
							
							if id_commenter in self.user_info[author]["user_connections"]: #has this user-user interaction been previously recorded 
								#we are not interested in the author commenting on themselves

								#save the type of relationship as well as the index of the commmenter. In this case the relationship between the author and the commentator is a
								#the thread_count represents the thread_id within the community
								#the i+1 represents the relative position between the author (user of interest) and the other user
								#IMPORTANT: positive distances between users mean that user_2 is commenting after the user of interest

								#change thread_count to thread name
								self.user_info[author]["user_connections"][id_commenter].append(('a', self.thread_count,i+1)) 
							
							else:
								self.user_info[author]["user_connections"][id_commenter]=[('a', self.thread_count,i+1)] # first initialize the list, save the type of relationship as well as the index of the commmenter


					#NOW we focus on the building interactions that involve commenting users being the users of interest

					for i in range(len(commenters_ids)):

						id_commenter=commenters_ids[i] #user of interest

						if id_commenter not in self.all_user_id_list: # has the user of interest been seen before?
							self.all_user_id_list.append(id_commenter) #add user of interest to list of recorded users
							
							#establish datastructure for user
							self.user_info[id_commenter]={} 
							self.user_info[id_commenter]["user_connections"]={}
							self.user_info[id_commenter]['community']=1
							self.user_info[id_commenter]['interaction_status']=0
							self.user_count+= 1 #count the user


						#connect the user of interest with the author (negative distance because user is commenting with author's post)

						if author!=id_commenter: #ensure the user is not the author to avoid interaction redundancy
							if author in self.user_info[id_commenter]["user_connections"]: #if this already exists
								#save the type of relationship as well as the index of the commmenter
								self.user_info[id_commenter]["user_connections"][author].append(('a', self.thread_count,-(i+1)))
							else:
								# first initialize the list, save the type of relationship as well as the index of the commmenter
								self.user_info[id_commenter]["user_connections"][author]=[('a', self.thread_count,-(i+1))] 


						#record all user/user interactions, positive distance means that user_j has commented after user_i. 
						if len(commenters_ids)>1: #if there are more than one user in the post
							for j in range(len(commenters_ids)): #iterate through all users  
								id_commenter_j= commenters_ids[j] #second user 
								if id_commenter_j in self.user_info[id_commenter]["user_connections"]: #if this already exists
									if id_commenter!=id_commenter_j: #we are not interested in the author commenting on themselves
										#save the type of relationship as well as the index of the commmenter
										self.user_info[id_commenter]["user_connections"][id_commenter_j].append(('c', self.thread_count,j-i)) 
								else:
									if id_commenter!=id_commenter_j:
										# first initialize the list, save the type of relationship as well as the index of the commmenter
										self.user_info[id_commenter]["user_connections"][id_commenter_j]=[('c', self.thread_count,j-i)] 

	def get_hash_user_id(self):

		cnt=0 #counter
		self.user_name_list=[]
		for user_name_i in list(self.user_info.keys()):
			self.hash_user_id[user_name_i]=cnt
			self.user_name_list.append(user_name_i)
			cnt+=1

	def assign_community_status(self):

		self.users_community_status=[]
		for user_name_i in list(self.user_info.keys()):
			self.users_community_status.append(self.user_info[user_name_i]["community"])
			
	def assign_interaction_status(self):
		self.users_interaction_status=[]
		for user_name_i in list(self.user_info.keys()):
			self.users_interaction_status.append(self.user_info[user_name_i]["interaction_status"])

	def connection_attribute_collection(self,connections_list, attr_index): #collects all of the attributes
		attr_list= [single_connection[attr_index] for single_connection in connections_list]
		return attr_list


	#calculate the distance decay between two functions

	def distance_decay_function(self,connection_distances_list,connection_types_list,a_weight_pheta=[1,1],c_weight_pheta=[1,1]):
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


	def get_connection_weights(self):
		print("Configuring Weights...")

		self.id_pairs=[] # list of tuples of connection id's
		self.pair_weight=[] #list of weights for each id_pair
		cnt=0


		for user_name_i in list(self.user_info.keys()):
			cnt+=1
			if cnt%500==0: 
				print(cnt," out of ", self.user_count)
			user_i_connections=self.user_info[user_name_i]["user_connections"] #get the connections of user i

			for user_name_j in list(user_i_connections.keys()): #iterate through connected users of user_i
				
				connection_instances=user_i_connections[user_name_j] #find the connection instances between user i and user j 
				
				
				threads_visited=[]#number of different threads a connection has been to


				#connection thread id number
				threads_visited=self.connection_attribute_collection(connections_list=connection_instances, attr_index=1) #sum of the connections distances
				unique_threads_visited=list(set(threads_visited))#get the unique threads visited
				thread_score_factor=1 #scale the score based on the number of unique threads visited? for now keep it as 1


				#author-commenter or commenter-commenter relationship
				connection_types=self.connection_attribute_collection(connections_list=connection_instances, attr_index=0) 
				
				#relative disance between two commenters
				distances=self.connection_attribute_collection(connections_list=connection_instances, attr_index=2) 
				
				distances_decay= self.distance_decay_function(connection_distances_list=distances,
														connection_types_list=connection_types,
														a_weight_pheta=[1,1],
														c_weight_pheta=[1,1]) #score of the strength and direction of the pair



				connection_score_sum=np.sum(np.asarray(thread_score_factor*distances_decay))#sum the non abs score terms
				connection_score_abs_sum=np.sum(np.abs(np.asarray(thread_score_factor*distances_decay))) #sum the abs score terms of each score

				weight_score= connection_score_abs_sum
				
				
				#we should add more complicated connections depending on the distance between commentators, order of comment, and the activity level of the author

				user_id_i=self.hash_user_id[user_name_i]#get the user hash id number
				user_id_j=self.hash_user_id[user_name_j]#get the user hash id number

				if connection_score_sum>0:
					self.id_pairs.append((user_id_i,user_id_j))#get the pair id pairs
					self.pair_weight.append(weight_score)

				#import pdb; pdb.set_trace()
		print("Finished Configuring Weights")

######################	CREATE THE FLIGHT NETWORK############################


class Social_Graph(Community): 
	def __init__(self,starting_year=2016, 
				starting_month= 1, 
				ending_year= 2016, 
				ending_month= 3,
				subreddit="kitesurfing",
				all_threads=None):
		
		super().__init__(starting_year,starting_month,ending_year, ending_month,subreddit,all_threads)

		self.interlink_score={}
		self.Generate_Graph() #create social network


	def Calculate_Loyalty(self):
		#get list of vs_ids

		vs_id_list=[vs_id.index for vs_id in VertexSeq(self.social_network)]

		loyalty_score_list=[]

		for vs_id in vs_id_list:
			#get edge id list for vertex
			es_id_list=[es.index for es in self.social_network.es.select(_source=vs_id)]

			#sum over all the weights connected to the vertex (edge weights)
			loyalty_score=sum([self.social_network.es['weight'][es_id] for es_id in es_id_list])
			
			#append to loyalty list
			loyalty_score_list.append(loyalty_score)

		return loyalty_score_list

	def Generate_Graph(self, update= False, generate=False):
		print("Creating Graph")
		if not update: 
			generate=True

		if generate: #default graph, do not update
			self.social_network=Graph(directed=False)
			self.social_network.add_vertices(self.user_count)
			self.social_network.add_edges(self.id_pairs)


			self.social_network.vs["name"]= self.user_name_list#assign each of the names of each node as teh 3 letter code for the airport
	

			self.social_network.es["weight"]= self.pair_weight #add the weights

			self.social_network.vs["degree"]=self.get_nodes_degree(range(self.user_count))

			self.social_network.vs["loyalty"]=self.Calculate_Loyalty()

			#get the 
		#social_network.vs["label"]=social_network.vs["name"]

		

		self.social_network.vs["interaction_status"]=self.users_interaction_status


		self.social_network.vs["community"]=self.users_community_status

		print("Finished Creating Graph")
	#take out all the unconnected nodes

	def get_nodes_degree(self,input_node_id_list): #get the degree of each of the nodes
		return self.social_network.degree(input_node_id_list)

	def get_degree(self,input_node_id):
		return
	def trim_unconnected_nodes(self): #trims unconnected nodes
		print("Removing unconnected nodes...")
		self.social_network_degree=self.get_nodes_degree(range(self.user_count)) #
		delete_vid_list=[]
		for vid in range(len(self.social_network_degree)):
			if self.social_network_degree[vid]==0:
				delete_vid_list.append(vid)
		self.social_network.delete_vertices(delete_vid_list)

	

	def get_inter_linkscore(self,
							input_node_id_list=[],
							max_degree=10,
							output_return=False):
		
		self.interlink_score={}
		for deg in range(1,max_degree+1):

			self.interlink_score[deg]=len(self.social_network.neighborhood(vertices=input_node_id_list,order=deg)[0])

		if output_return:
			return self.interlink_score



	def get_inter_neighbor_degree(self,
									input_node_id_list=[],
									max_degree=10,
									 output_return=False): #get the degree of the connected neibhrours of th
		self.inter_neighbor_degree={}

		for deg in range(1,max_degree+1):
			#get neigbhours within specfic path length
			neighbor_nodes=self.social_network.neighborhood(vertices=input_node_id_list,order=deg)[0]
			self.inter_neighbor_degree[deg]=self.get_nodes_degree(neighbor_nodes)
		
		if output_return:
			return self.inter_neighbor_degree



	def update_community(self):
		self.assign_community_status()
		self.assign_interaction_status()
		self.Generate_Graph(update=True)


	def print_graph(self, verbose=False):
		self.trim_unconnected_nodes()
		print("Printing graph")
		visual_style = {}
		visual_style["vertex_size"] = 5

		vertex_color=[]
		
		for i in range(len(self.social_network.vs["community"])):
			if self.social_network.vs["community"][i]==1:
				vertex_color.append('red')
			if self.social_network.vs["community"][i]==2:
				vertex_color.append('blue')


			if self.social_network.vs['interaction_status'][i]==1:
				vertex_color[i]='green'

		visual_style["vertex_color"] = vertex_color
		if verbose:
			visual_style["vertex_label"] = self.social_network.vs["name"]

		#visual_style["edge_width"] = self.social_network.es["weight"]
		visual_style["layout"]=self.social_network.layout("kk")
		plot(self.social_network, **visual_style)






