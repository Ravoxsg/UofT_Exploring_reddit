# Plots properties of graphs of community pairs

import pickle
import os 
import pdb, traceback, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


#matplotlib.use('Qt4Agg')
plt.ion()

filename='community_outputs/interaction_info_output_2000'
with open(filename,'rb') as fp:
	output= pickle.load(fp)

def get_key_pairs(group_specific_output):
	key_pairs=[]
	outer_key_list=list(group_specific_output.keys())

	for outer_key in outer_key_list:
		inner_key_list=list(group_specific_output[outer_key].keys())
		for inner_key in inner_key_list:
			key_pairs.append([outer_key,inner_key])

	return key_pairs

#figure 1 inter users ratio
inter_users_ratio={}

#degree of each of the inter-users
inter_user_degree={}
inter_user_k_shell={}

user_inter_link_score={}
user_inter_neighbor_degree={}
user_inter_neighbor_k_shell={}

group_type_list=list(output.keys())

try:

	for group_type in group_type_list:

		group_specific_output=output[group_type]
		comm_pair_list=get_key_pairs(group_specific_output)

		# list of values
		inter_users_ratio[group_type]={}
		inter_users_ratio[group_type]['group_1']=[]
		inter_users_ratio[group_type]['group_2']=[]
		inter_users_ratio[group_type]['both']=[]

		#list of degrees
		inter_user_degree[group_type]={}

		inter_user_degree[group_type]['group_1']=[]
		inter_user_degree[group_type]['group_2']=[]
		inter_user_degree[group_type]['both']=[]

		inter_user_k_shell[group_type]={}

		inter_user_k_shell[group_type]['group_1']=[]
		inter_user_k_shell[group_type]['group_2']=[]
		inter_user_k_shell[group_type]['both']=[]

		user_inter_neighbor_k_shell[group_type]={}

		user_inter_neighbor_k_shell[group_type]['group_1']={}
		user_inter_neighbor_k_shell[group_type]['group_2']={}
		user_inter_neighbor_k_shell[group_type]['both']={}

		#list of 
		user_inter_link_score[group_type]={}

		user_inter_link_score[group_type]['group_1']={}
		user_inter_link_score[group_type]['group_2']={}
		user_inter_link_score[group_type]['both']={}

		user_inter_neighbor_degree[group_type]={}

		user_inter_neighbor_degree[group_type]['group_1']={}
		user_inter_neighbor_degree[group_type]['group_2']={}
		user_inter_neighbor_degree[group_type]['both']={}

		for comm_1, comm_2 in comm_pair_list:

			pair_output=group_specific_output[comm_1][comm_2]
			
			#get ratio of inter-users

			inter_users_ratio[group_type]['group_1'].append(pair_output['num_inter_users']/pair_output['num_users']['group_1'])
			inter_users_ratio[group_type]['group_2'].append(pair_output['num_inter_users']/pair_output['num_users']['group_2'])
			inter_users_ratio[group_type]['both'].append(pair_output['num_inter_users']/(pair_output['num_users']['group_1']+pair_output['num_users']['group_2']))		

			#get inter user degree 

			for measure_type in ['group_1','group_2']:
				inter_user_degree[group_type][measure_type]=inter_user_degree[group_type][measure_type]+pair_output['inter_degree'][measure_type]
				inter_user_degree[group_type]['both']=inter_user_degree[group_type]['both']+pair_output['inter_degree'][measure_type]

			#user-inter-neibhor-degree

			for measure_type in ['group_1','group_2']:
				for inter_user_output in  pair_output['user_inter_neighbor_degree'][measure_type]:
					degree_key_list=list(inter_user_output.keys()) #get keys of degree
					for degree_key in degree_key_list: #iterate through each degree 
						if degree_key in list(user_inter_neighbor_degree[group_type][measure_type].keys()):
							user_inter_neighbor_degree[group_type][measure_type][degree_key]= user_inter_neighbor_degree[group_type][measure_type][degree_key]+ inter_user_output[degree_key]
							user_inter_neighbor_degree[group_type]['both'][degree_key]=user_inter_neighbor_degree[group_type]['both'][degree_key]+inter_user_output[degree_key]
						else: 
							user_inter_neighbor_degree[group_type][measure_type][degree_key]=inter_user_output[degree_key]
							user_inter_neighbor_degree[group_type]['both'][degree_key]=inter_user_output[degree_key]

			#get inter user k-shell 

			for measure_type in ['group_1','group_2']:
				inter_user_k_shell[group_type][measure_type]=inter_user_k_shell[group_type][measure_type]+pair_output['inter_k_shell'][measure_type]
				inter_user_k_shell[group_type]['both']=inter_user_k_shell[group_type]['both']+pair_output['inter_k_shell'][measure_type]

			#user-inter-neibhor-k-shell

			for measure_type in ['group_1','group_2']:
				for inter_user_output in  pair_output['user_inter_neighbor_k_shell'][measure_type]:
					degree_key_list=list(inter_user_output.keys()) #get keys of degree
					for degree_key in degree_key_list: #iterate through each degree 
						if degree_key in list(user_inter_neighbor_k_shell[group_type][measure_type].keys()):
							user_inter_neighbor_k_shell[group_type][measure_type][degree_key]= user_inter_neighbor_k_shell[group_type][measure_type][degree_key]+ inter_user_output[degree_key]
							user_inter_neighbor_k_shell[group_type]['both'][degree_key]=user_inter_neighbor_k_shell[group_type]['both'][degree_key]+inter_user_output[degree_key]
						else: 
							user_inter_neighbor_k_shell[group_type][measure_type][degree_key]=inter_user_output[degree_key]
							user_inter_neighbor_k_shell[group_type]['both'][degree_key]=inter_user_output[degree_key]

			#user-inter-link-score
			for measure_type in ['group_1','group_2']:
				for inter_user_output in  pair_output['user_inter_link_score'][measure_type]:
					degree_key_list=list(inter_user_output.keys()) #get keys of degree
					for degree_key in degree_key_list: #iterate through each degree 
						if degree_key in list(user_inter_link_score[group_type][measure_type].keys()):
							user_inter_link_score[group_type][measure_type][degree_key]= user_inter_link_score[group_type][measure_type][degree_key]+ [inter_user_output[degree_key]/pair_output['num_users'][measure_type]]
							user_inter_link_score[group_type]['both'][degree_key]=user_inter_link_score[group_type]['both'][degree_key]+[inter_user_output[degree_key]/pair_output['num_users'][measure_type]]
						else: 
							user_inter_link_score[group_type][measure_type][degree_key]=[inter_user_output[degree_key]/pair_output['num_users'][measure_type]]
							user_inter_link_score[group_type]['both'][degree_key]=[inter_user_output[degree_key]/pair_output['num_users'][measure_type]]

except : 

	type, value, tb = sys.exc_info()
	traceback.print_exc()
	pdb.post_mortem(tb)

print("Done Fucker")


#print figure 1: 

group_key_list=['random','similar','conflict']

###############################################################################################################

#figure 1 inter users ratio

"""

#group_key_list=list(inter_users_ratio.keys())
inter_users_ratio_mean=[np.mean(np.array((inter_users_ratio[group_key]['both']))) for group_key in group_key_list]
inter_users_ratio_std=[np.std(np.array((inter_users_ratio[group_key]['both']))) for group_key in group_key_list]

fig, ax = plt.subplots()
x=group_key_list
y=inter_users_ratio_mean
ax.bar(x, y, 0.35, color='r')
ax.errorbar(x, y, yerr=inter_users_ratio_std, fmt='o')
ax.set_title('Proportion of Interactive Users')

"""

###############################################################################################################

#figure 2 inter degree

"""

# the histogram of the data
x_c=inter_user_degree['conflict']['both']
x_r= inter_user_degree['random']['both']
x_s= inter_user_degree['similar']['both']

labels=['similar','random', 'conflict']
colors=['g','r', 'b']
x=[x_s,x_r,x_c]

plt.hist(x, 30, density=True, alpha=0.75, label=labels, color=colors)
plt.legend(loc='upper right')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.title('Degree of Interactive Users')
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show(block=False)

"""

###############################################################################################################

#figure 3

"""

degree_key_list=list(user_inter_link_score['random']['both'].keys())

user_inter_link_mean={}
user_inter_link_std={}
for group_key in group_key_list:
	user_inter_link_mean[group_key]=[np.mean(np.array(user_inter_link_score[group_key]['both'][degree_key])) for degree_key in degree_key_list ]
	user_inter_link_std[group_key]=[np.std(np.array(user_inter_link_score[group_key]['both'][degree_key])) for degree_key in degree_key_list ]

x= [degree_key_list,degree_key_list, degree_key_list]
y=[user_inter_link_mean['random'], user_inter_link_mean['similar'],user_inter_link_mean['conflict']]
colors=['r','g','b']
y_std=[user_inter_link_std['random'], user_inter_link_std['similar'],user_inter_link_std['conflict']]

x=np.array(x)
y=np.array(y)
y_std=np.array(y_std)

plt.plot(x[0], y[0], 'k', color='#CC4F1B')
plt.fill_between(x[0], y[0]-y_std[0], y[0]+y_std[0], alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848')

plt.plot(x[1], y[1], 'k', color='#1B2ACC')
plt.fill_between(x[1], y[1]-y_std[1], y[1]+y_std[1], alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF', linewidth=4, linestyle='dashdot', antialiased=True)

plt.plot(x[2], y[2], 'k', color='#3F7F4C')
plt.fill_between(x[2], y[2]-y_std[2], y[2]+y_std[2], alpha=1, edgecolor='#3F7F4C', facecolor='#7EFF99', linewidth=0)

plt.xlabel('Order')
plt.ylabel('Proportion of Users')
plt.title('Community Proportion Connected with Interactive Users')
plt.axis([0, 10, 0, 1])
plt.grid(True)
plt.legend(loc='upper right')
plt.show(block=False)

"""

###############################################################################################################

#figure 4 inter user neighborhood degree


###############################################################################################################

#figure 5

"""

x_c=inter_user_k_shell['conflict']['both']
x_r= inter_user_k_shell['random']['both']
x_s= inter_user_k_shell['similar']['both']

labels=['similar','random','conflict']
colors=['g','r','b']
x=[x_s,x_r,x_c]

plt.hist(x, 30, density=True, alpha=0.75,label=labels, color=colors)
plt.legend(loc='upper right')
plt.xlabel('K-Shell')
plt.ylabel('Frequency')
plt.title('K-Shell of Interactive Users')
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show(block=False)

"""

###############################################################################################################

#figure 6

"""

order=2
x_s=user_inter_neighbor_k_shell["similar"]['both'][order]
x_r=user_inter_neighbor_k_shell["random"]['both'][order]
x_c=user_inter_neighbor_k_shell["conflict"]['both'][order]

# the histogram of the data

labels=['similar','conflict','random']
colors=['g','b','r']
x=[x_s,x_c,x_r]

plt.hist(x, 30, density=True, alpha=0.75,label=labels, color=colors)
plt.legend(loc='upper right')
plt.xlabel('Shell')
plt.ylabel('Freqeuncy')
plt.title('K-Shell of Interactive User Neighbours (Order = '+str(order)+')')
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show(block=False)

"""

###############################################################################################################


pdb.set_trace()

