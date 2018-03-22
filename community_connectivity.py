from graph_tools import *
import pdb

def find_common_elements(list1,list2):
	return list(set(list1).intersection(list2))

def user_community_assign(list_a,list_b):
	return list(map(lambda x,y:int(x>y), list_a, list_b))

if __name__ == '__main__':

	group_1= Social_Graph(subreddit="prolife",
	 						starting_year=2016, 
	 						starting_month= 1, 
	 						ending_year= 2016,
	 						 ending_month= 3)

	group_2= Social_Graph(subreddit="prochoice",
	 						starting_year=2016, 
	 						starting_month= 1, 
	 						ending_year= 2016,
	 						 ending_month= 3)

	#find common interacting users
	group_2.inter_group_users_name=group_1.inter_group_users_name= \
	find_common_elements(group_1.all_user_id_list,group_2.all_user_id_list)
	
	#get user ids of interacting users within each group (they will be different for each group)
	group_1.inter_group_users_id= [group_1.hash_user_id[user_name] for user_name in group_1.inter_group_users_name]
	group_2.inter_group_users_id= [group_2.hash_user_id[user_name] for user_name in group_2.inter_group_users_name]

	#get loyalty scores for each memeber for each group
	group_1.inter_group_users_loyalty=[group_1.social_network.vs.select(name_eq=user_name)['loyalty'][0] for user_name in group_1.inter_group_users_name]
	group_2.inter_group_users_loyalty=[group_2.social_network.vs.select(name_eq=user_name)['loyalty'][0] for user_name in group_2.inter_group_users_name]

	#infer community assginmet for loyalty scores
	group_1.inter_group_users_community=user_community_assign(group_1.inter_group_users_loyalty, group_2.inter_group_users_loyalty )
	group_2.inter_group_users_community=user_community_assign(group_2.inter_group_users_loyalty, group_1.inter_group_users_loyalty )


	#updpate community assignments for intereactions
	for i in range(len(group_1.inter_group_users_id))
		group_1.users_community[group_1.inter_group_users_id[i]]=group_1.inter_group_users_community[i]
		group_2.users_community[group_2.inter_group_users_id[i]]=group_2.inter_group_users_community[i]

	group_1.social_network.vs['community']=group_1.users_community
	group_2.social_network.vs['community']=group_2.users_community



	pdb.set_trace()


