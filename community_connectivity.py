from graph_tools import *
import os
import pdb, traceback, sys
import re
def find_common_elements(list1,list2):
	return list(set(list1).intersection(list2))

def user_community_assign(list_a,list_b):
	return list(map(lambda x,y:int(x>y), list_a, list_b))


main_dir=os.getcwd()


def get_graph(subreddit_name,starting_year, starting_month, ending_year,ending_month,user_limit, all_threads=None):
	
	os.chdir(main_dir)
	output_folder='community_graphs/'
	
	file_name=output_folder+subreddit_name+"_"+str(user_limit)+"_graph.pickle"
	
	user_limit_file=0
	if os.path.isfile(file_name):
		
		user_limit_file=int(re.search(r'\d+', file_name).group())

	

	if os.path.isfile(file_name) and user_limit_file>=user_limit:
		#load file
		with open(file_name,'rb') as f: 
			group=pickle.load(f)

		

		return group

	else:
		if all_threads == None:
			all_threads=merge_threads(subreddit_name, starting_year, starting_month, ending_year, ending_month)

		group= Social_Graph(subreddit=subreddit_name,
		 						starting_year=starting_year, 
		 						starting_month= starting_month, 
		 						ending_year= ending_year,
		 						 ending_month= ending_month,
		 						 all_threads=all_threads,
		 						 user_count_limit=user_limit)
		#save file
		os.chdir(main_dir)
		with open(file_name,'wb') as f:
			pickle.dump(group,f)

		

		return group



	

def compare_communities(subreddit_1="prolife",subreddit_2="prochoice",
						group_type='conflict',
						save_results=True,
						year_interval=[2016,2016],
						month_interval=[1,7],
						print_community_graphs=False,
						print_merged_community=False,
						user_limit=1000,
						subsample_size=100,
						save_data=True,
						group_merge_bool=True):

	#make subreddit one the higher order
	subreddit_1,subreddit_2=sorted([subreddit_1,subreddit_2])

	starting_year,ending_year=year_interval
	starting_month, ending_month=month_interval
	#combine both threads

	print("Collecting Threads: ", subreddit_1)


	group_1=get_graph(subreddit_1, starting_year, starting_month, ending_year, ending_month,user_limit)


	print("Collecting Threads: ", subreddit_2)


	group_2=get_graph(subreddit_2, starting_year, starting_month, ending_year, ending_month,user_limit)

	

	if group_1.user_count==0 or group_2.user_count==0:
		return


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
	

	if group_merge_bool:
		all_threads_1=group_1.all_threads[0:group_1.thread_limit]
		all_threads_2=group_2.all_threads[0:group_2.thread_limit]
		all_threads=all_threads_1+all_threads_2
		group_merge=Social_Graph(subreddit=subreddit_1,
		 						starting_year=starting_year, 
		 						starting_month= starting_month, 
		 						ending_year= ending_year,
		 						 ending_month= ending_month,
		 						 all_threads=all_threads)

		#reassign user name community commitments from both merged groups



		for user_name in group_1.user_name_list:
			group_merge.user_info[user_name]["community"]=1

		for user_name in group_2.user_name_list:
			group_merge.user_info[user_name]["community"]=2


		for user_name in group_1.inter_group_users_name:
			group_merge.user_info[user_name]["interaction_status"]=1

		group_merge.update_community() #update the user_id based interactions status


	#Saving the DATA

	#check if file exists
	os.chdir(main_dir)

	print('Saving Interaction Data')
	output_folder='community_outputs/'
	interaction_info_output_filename='interaction_info_output_'+str(user_limit)
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
			interaction_info_output['control_similar']={}
			interaction_info_output['control_random']={}
	else: 

		#if doesnt exist, create it
		interaction_info_output={}
		interaction_info_output['random']={}
		interaction_info_output['conflict']={}
		interaction_info_output['similar']={}
		interaction_info_output['control_similar']={}
		interaction_info_output['control_random']={}	


	pair_dict_keys=list(interaction_info_output[group_type].keys())

	#remember (subreddit_1,subreddit_2=sorted([subreddicot_1,subreddit_2]))
	#create a new instance of the saved interaction

	#NOTICE: MAYBE WE DONT NEED THIS DUE TO ALPHABETICAL ORDERING
	if subreddit_1 in pair_dict_keys: #check the first group as the subreddit_1 as it should exist
		interaction_info_output[group_type][subreddit_1]={}
		interaction_info_output[group_type][subreddit_1][subreddit_2]={}
	else: #interaction doesnt exist because subbreddit_2 is not in front of subreddit_1 due to alphabetical ordering
		interaction_info_output[group_type][subreddit_1]={}
		interaction_info_output[group_type][subreddit_1][subreddit_2]={}


	#number of users
	num_users={}
	num_users['group_1']=group_1.user_count
	num_users['group_2']=group_2.user_count
	interaction_info_output[group_type][subreddit_1][subreddit_2]['num_users']=num_users



	#first we want to get the number of interacting users

	interaction_info_output[group_type][subreddit_1][subreddit_2]['num_inter_users']=num_inter_users


	inter_degree={}
	inter_degree['group_1']=group_1.get_nodes_degree(group_1.inter_group_users_id)
	inter_degree['group_2']=group_2.get_nodes_degree(group_2.inter_group_users_id)
	interaction_info_output[group_type][subreddit_1][subreddit_2]['inter_degree']=inter_degree

	inter_k_shell={}
	inter_k_shell['group_1']=group_1.get_nodes_k_shell(group_1.inter_group_users_id)
	inter_k_shell['group_2']=group_2.get_nodes_k_shell(group_2.inter_group_users_id)
	interaction_info_output[group_type][subreddit_1][subreddit_2]['inter_k_shell']=inter_k_shell




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

	inter_neighbor_degree['group_1']=group_1.get_inter_neighbor_degree(group_1.inter_group_users_id,max_path_length,True)
	inter_neighbor_degree['group_2']=group_2.get_inter_neighbor_degree(group_2.inter_group_users_id,max_path_length,True)


	interaction_info_output[group_type][subreddit_1][subreddit_2]["inter_neighbor_degree"]=inter_neighbor_degree


	#Get the User Level inter-link-score

	user_inter_neighbor_degree={}
	max_path_length=10 #we want the market to saturate
	user_inter_neighbor_degree['group_1']=[group_1.get_inter_neighbor_degree([inter_user_id],max_path_length,True) \
										for inter_user_id in group_1.inter_group_users_id]
	user_inter_neighbor_degree['group_2']=[group_2.get_inter_neighbor_degree([inter_user_id],max_path_length,True) \
										for inter_user_id in group_2.inter_group_users_id]

	interaction_info_output[group_type][subreddit_1][subreddit_2]["user_inter_neighbor_degree"]=user_inter_neighbor_degree


	#GET THE INTER NEIGBHOR DEGREE SCORE 
	inter_neighbor_k_shell={}
	max_path_length=3

	inter_neighbor_k_shell['group_1']=group_1.get_inter_neighbor_k_shell(group_1.inter_group_users_id,max_path_length,True)
	inter_neighbor_k_shell['group_2']=group_2.get_inter_neighbor_k_shell(group_2.inter_group_users_id,max_path_length,True)


	interaction_info_output[group_type][subreddit_1][subreddit_2]["inter_neighbor_k_shell"]=inter_neighbor_k_shell


	#Get the User Level inter-link-score

	user_inter_neighbor_k_shell={}
	max_path_length=10 #we want the market to saturate
	user_inter_neighbor_k_shell['group_1']=[group_1.get_inter_neighbor_k_shell([inter_user_id],max_path_length,True) \
										for inter_user_id in group_1.inter_group_users_id]
	user_inter_neighbor_k_shell['group_2']=[group_2.get_inter_neighbor_k_shell([inter_user_id],max_path_length,True) \
										for inter_user_id in group_2.inter_group_users_id]

	interaction_info_output[group_type][subreddit_1][subreddit_2]["user_inter_neighbor_k_shell"]=user_inter_neighbor_k_shell





	with open(file_name,'wb') as fp: 
		pickle.dump(interaction_info_output,fp)


	#pdb.set_trace()

	print("Saved Individual Community Data")
	print('Saving Interaction Data')


	#BORING PRINTING STUFF

	if print_community_graphs:
		group_1.print_graph()
		group_2.print_graph()

	if print_merged_community and group_merge_bool:
		group_merge.print_graph()

import os




with open("sport_pairs.pickle",'rb') as fp: 
	pairs_index=pickle.load(fp)

'''
pairs_index={'random': [['prolife', 'PurplePillDebate'], ['prochoice', 'climate'], ['The_Donald', 'prohealth'], ['HillaryForAmerica', 'Anarchism'], ['Feminism', 'prohealth'], ['TheRedPill', 'climate'], ['climatechange', '2016_elections'], ['climateskeptics', '2016_elections']], 
			'control_random': [['Calligraphy', 'bookbinding']], 'control_similar': [['Calligraphy', 'bookbinding']], 
			'similar': [['prolife', 'prohealth'], ['prolife', 'prohealth'], ['The_Donald', '2016_elections'], ['HillaryForAmerica', '2016_elections'], ['Feminism', 'Anarchism'], ['TheRedPill', 'PurplePillDebate'], ['climatechange', 'climate'], ['climateskeptics', 'climate'], ['Feminism','prochoice']],
			'conflict': [['prolife', 'prochoice'], ['The_Donald', 'HillaryForAmerica'], ['Feminism', 'TheRedPill'], ['climatechange', 'climateskeptics'], ['Feminism','prolife']]}

pairs_index={'similar': [['prochoice', 'Calligraphy']]}
'''
pdb.set_trace()


group_type_list=list(pairs_index.keys())


avoided_subreddits=["The_Donald"]


for group_type in group_type_list: 
	pair_list=pairs_index[group_type]
	print(group_type)

	for pair in pair_list:

		print("Subreddit 1: ", pair[0], "Subreddit 2: ", pair[1])

		if pair[0] not in avoided_subreddits and pair[1] not in avoided_subreddits:
		

			try:
				compare_communities(subreddit_1=pair[0],subreddit_2=pair[1],
								group_type=group_type,
								save_results=True,
								year_interval=[2016,2016],
								month_interval=[1,10],
								print_community_graphs=False,
								print_merged_community=False,
								user_limit=1000,
								subsample_size=400,
								save_data=True,
								group_merge_bool=False)
			except : 

				
				type, value, tb = sys.exc_info()
				traceback.print_exc()
				pdb.post_mortem(tb)
			



