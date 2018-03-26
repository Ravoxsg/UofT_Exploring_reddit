from graph_tools import *
import pdb

def find_common_elements(list1,list2):
	return list(set(list1).intersection(list2))

def user_community_assign(list_a,list_b):
	return list(map(lambda x,y:int(x>y), list_a, list_b))

starting_year=2016
starting_month=1
ending_year=2016
ending_month=3






if __name__ == '__main__':

	#starting at a new thread_idx
	thread_idx=[0,100]
	#get threads from

	#combine both threads

	subreddit_1="prolife"

	all_threads_1=merge_threads(subreddit_1, starting_year, starting_month, ending_year, ending_month)
	all_threads_1=all_threads_1[thread_idx[0]:thread_idx[1]]

	group_1= Social_Graph(subreddit=subreddit_1,
	 						starting_year=starting_year, 
	 						starting_month= starting_month, 
	 						ending_year= ending_year,
	 						 ending_month= ending_month,
	 						 all_threads=all_threads_1)

	subreddit_2="prochoice"

	all_threads_2=merge_threads(subreddit_2, starting_year, starting_month, ending_year, ending_month)
	all_threads_2=all_threads_2[thread_idx[0]:thread_idx[1]]

	group_2= Social_Graph(subreddit=subreddit_2,
	 						starting_year=starting_year, 
	 						starting_month= starting_month, 
	 						ending_year= ending_year,
	 						 ending_month= ending_month,
	 						 all_threads= all_threads_2)
	group_1.print_graph()
	group_2.print_graph()
	#find common interacting users
	group_2.inter_group_users_name=group_1.inter_group_users_name= \
	find_common_elements(group_1.all_user_id_list,group_2.all_user_id_list)
	
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
	for user_name in group_1.user_name_list:
		group_merge.user_info[user_name]["community"]=1

	for user_name in group_2.user_name_list:
		group_merge.user_info[user_name]["community"]=2

	group_merge.assign_community_status()

	#update the user_id based community status

	for user_name in group_1.inter_group_users_name:
		group_merge.user_info[user_name]["interaction_status"]=1

	
	group_merge.assign_community_status()
	group_merge.assign_interaction_status()

	#pdb.set_trace()

	group_merge.Generate_Graph(update=True)
	
	#update the user_id based interactions status

	print(group_2.inter_group_users_name)

	#group_merge.Generate_Graph(update=True) #we want to update the graph given the community  and interaction status

	group_merge.print_graph()
	#we need to convert the community scores from group1 and group2 to the final group 






