from graph_tools import *
import os
import pdb

def find_common_elements(list1,list2):
	return list(set(list1).intersection(list2))

def user_community_assign(list_a,list_b):
	return list(map(lambda x,y:int(x>y), list_a, list_b))

starting_year=2016
starting_month=1
ending_year=2016
ending_month=3


main_dir=os.getcwd()

def compare_communities(subreddit_1="prolife",subreddit_2="prochoice",
						group_type='conflict',
						save_results=True,
						year_interval=[2016,2016],
						month_interval=[1,9],
						print_community_graphs=False,
						print_merged_community=False,
						thread_idx=[0,100000]):

	#make subreddit one the higher order
	subreddit_1,subreddit_2=sorted([subreddit_1,subreddit_2])

	starting_year,ending_year=year_interval
	starting_month, ending_month=month_interval
	#combine both threads

	all_threads_1=merge_threads(subreddit_1, starting_year, starting_month, ending_year, ending_month)
	#all_threads_1=all_threads_1[thread_idx[0]:thread_idx[1]]

	group_1= Social_Graph(subreddit=subreddit_1,
	 						starting_year=starting_year, 
	 						starting_month= starting_month, 
	 						ending_year= ending_year,
	 						 ending_month= ending_month,
	 						 all_threads=all_threads_1)


	all_threads_2=merge_threads(subreddit_2, starting_year, starting_month, ending_year, ending_month)
	#all_threads_2=all_threads_2[thread_idx[0]:thread_idx[1]]

	group_2= Social_Graph(subreddit=subreddit_2,
	 						starting_year=starting_year, 
	 						starting_month= starting_month, 
	 						ending_year= ending_year,
	 						 ending_month= ending_month,
	 						 all_threads= all_threads_2)

	#find common interacting users
	group_2.inter_group_users_name=group_1.inter_group_users_name= \
	find_common_elements(group_1.all_user_id_list,group_2.all_user_id_list)

	#number of interacting users
	num_inter_users=len(group_2.inter_group_users_name)

	#get user ids of interacting users within each group (they will be different for each group)
	group_1.inter_group_users_id= [group_1.hash_user_id[user_name] for user_name in group_1.inter_group_users_name]
	group_2.inter_group_users_id= [group_2.hash_user_id[user_name] for user_name in group_2.inter_group_users_name]



	#get loyalty scores for each memeber for each group
	group_1.inter_group_users_loyalty=[group_1.social_network.vs.select(name_eq=user_name)['loyalty'] for user_name in group_1.inter_group_users_name]
	group_2.inter_group_users_loyalty=[group_2.social_network.vs.select(name_eq=user_name)['loyalty'] for user_name in group_2.inter_group_users_name]

	#infer community assginmet for loyalty scores
	group_1.inter_group_users_community=user_community_assign(group_1.inter_group_users_loyalty, group_2.inter_group_users_loyalty )
	group_2.inter_group_users_community=user_community_assign(group_2.inter_group_users_loyalty, group_1.inter_group_users_loyalty )


	#updpate community assignments for intereactions
	for i in range(len(group_1.inter_group_users_id)):
		group_1.users_community_status[group_1.inter_group_users_id[i]]=group_1.inter_group_users_community[i]
		group_2.users_community_status[group_2.inter_group_users_id[i]]=group_2.inter_group_users_community[i]



	group_1.social_network.vs['community']=group_1.users_community_status
	group_2.social_network.vs['community']=group_2.users_community_status


	#create the group merge
	all_threads=all_threads_1+all_threads_2

	group_merge=Social_Graph(subreddit=subreddit_1,
	 						starting_year=starting_year, 
	 						starting_month= starting_month, 
	 						ending_year= ending_year,
	 						 ending_month= ending_month,
	 						 all_threads=all_threads)

	#reassign user name community commitments from both merged groups
	


	try:
		for user_name in group_1.user_name_list:
			group_merge.user_info[user_name]["community"]=1
			print(user_name)

		for user_name in group_2.user_name_list:
			group_merge.user_info[user_name]["community"]=2
			print(user_name)
	except KeyError: 
		pdb.set_trace()

	for user_name in group_1.inter_group_users_name:
		group_merge.user_info[user_name]["interaction_status"]=1

	group_merge.update_community() #update the user_id based interactions status


	#Saving the DATA

	#check if file exists
	os.chdir(main_dir)

	community_info_output_filename='community_info_output'
	interaction_info_output_filename='interaction_info_output'
	output_folder='community_outputs/'

	file_name=output_folder+community_info_output_filename
	if os.path.isfile(file_name):
		try:
			with open(file_name,'rb') as fp:
				community_info_outputs=pickle.load(fp)
		except EOFError:
			community_info_outputs={}
	else: 

		#if doesnt exist, create it
		community_info_outputs={}

	community_info_outputs[subreddit_1]={}
	community_info_outputs[subreddit_1]['num_users']=group_1.user_count

	community_info_outputs[subreddit_2]={}
	community_info_outputs[subreddit_2]['num_users']=group_2.user_count


	with open(file_name,'wb') as fp: 
		pickle.dump(community_info_outputs,fp)


	print("Saved Individual Community Data")
	print('Saving Interaction Data')

	file_name=output_folder+interaction_info_output_filename
	if os.path.isfile(file_name):

		try:
			with open(file_name,'rb') as fp:
				interaction_info_output=pickle.load(fp)

		except EOFError:
			interaction_info_output={}
			interaction_info_output['random']={}
			interaction_info_output['conflict']={}
			interaction_info_output['similar']={}
	else: 

		#if doesnt exist, create it
		interaction_info_output={}
		interaction_info_output['random']={}
		interaction_info_output['conflict']={}
		interaction_info_output['similar']={}
		interaction_info_output['control_similar']={}
		interaction_info_output['control_random']={}	


	pair_dict_keys=list(interaction_info_output[group_type].keys())

	#remember (subreddit_1,subreddit_2=sorted([subreddit_1,subreddit_2]))
	#create a new instance of the saved interaction

	#NOTICE: MAYBE WE DONT NEED THIS DUE TO ALPHABETICAL ORDERING
	if subreddit_1 in pair_dict_keys: #check the first group as the subreddit_1 as it should exist
		interaction_info_output[group_type][subreddit_1]={}
		interaction_info_output[group_type][subreddit_1][subreddit_2]={}
	else: #interaction doesnt exist because subbreddit_2 is not in front of subreddit_1 due to alphabetical ordering
		interaction_info_output[group_type][subreddit_1]={}
		interaction_info_output[group_type][subreddit_1][subreddit_2]={}


	#first we want to get the number of interacting users

	interaction_info_output[group_type][subreddit_1][subreddit_2]['num_inter_users']=num_inter_users

	inter_degree={}
	inter_degree['group_1']=group_1.get_nodes_degree(group_1.inter_group_users_id)
	inter_degree['group_2']=group_2.get_nodes_degree(group_2.inter_group_users_id)
	interaction_info_output[group_type][subreddit_1][subreddit_2]['inter_degree']=inter_degree

	#GET THE LINK SCORE, number of users connected to the list of interacting users based on a specific path length
	inter_link_score={}
	max_path_length=10 #we want the market to saturate
	inter_link_score['group_1']=group_1.get_inter_linkscore(group_1.inter_group_users_id,max_path_length,True)
	inter_link_score['group_2']=group_2.get_inter_linkscore(group_2.inter_group_users_id,max_path_length,True)

	#attacth it to main dictionary
	interaction_info_output[group_type][subreddit_1][subreddit_2]["inter_link_score"]=inter_link_score
	

	#Get the User Level inter-link-score

	user_inter_link_score={}
	max_path_length=10 #we want the market to saturate
	user_inter_link_score['group_1']=[group_1.get_inter_linkscore([inter_user_id],max_path_length,True) \
										for inter_user_id in group_1.inter_group_users_id]
	user_inter_link_score['group_2']=[group_2.get_inter_linkscore([inter_user_id],max_path_length,True) \
										for inter_user_id in group_2.inter_group_users_id]

	interaction_info_output[group_type][subreddit_1][subreddit_2]["user_inter_link_score"]=user_inter_link_score



	#GET THE INTER NEIGBHOR DEGREE SCORE 
	inter_neighbor_degree={}
	max_path_length=3

	inter_neighbor_degree['group_1']=group_1.get_inter_neighbor_degree(max_path_length,True)
	inter_neighbor_degree['group_2']=group_2.get_inter_neighbor_degree(max_path_length,True)


	interaction_info_output[group_type][subreddit_1][subreddit_2]["inter_neighbor_degree"]=inter_neighbor_degree


	#Get the User Level inter-link-score

	user_inter_neighbor_degree={}
	max_path_length=10 #we want the market to saturate
	user_inter_neighbor_degree['group_1']=[group_1.get_inter_neighbor_degree([inter_user_id],max_path_length,True) \
										for inter_user_id in group_1.inter_group_users_id]
	user_inter_neighbor_degree['group_2']=[group_2.get_inter_neighbor_degree([inter_user_id],max_path_length,True) \
										for inter_user_id in group_2.inter_group_users_id]

	interaction_info_output[group_type][subreddit_1][subreddit_2]["user_inter_neighbor_degree"]=user_inter_neighbor_degree




	#BORING PRINTING STUFF

	if print_community_graphs:
		group_1.print_graph()
		group_2.print_graph()

	if print_merged_community:
		group_merge.print_graph()

import os

#os.chdir('community_outputs')
os.chdir('community_outputs')
print(os.path.isfile("bruh"))
compare_communities()




