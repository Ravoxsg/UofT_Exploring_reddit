import os
import numpy as np

community_group_types=["random","similar","conflict"]

community_pair_type="random" #three options
(1,2016)
(6,2016)

[()]

class Community:
	def __init__(start_month_year,
				end_month_year,
				custum_month_year_tuples,
				community_name, 
				pair_type):


		self.pair_type=pair_type #what assignment is this community going to be assigned to


		self.start_month_year=start_month_year 
		self.end_month_year= end_month_year
		self.custum_month_year_tuples= custum_month_year_tuples #get the custum month year tuples

		self.month_year_tuples=self.get_month_year_tuples() #get the year month tuples

	def get_year_month_tuples(self):


		if len(self.custum_month_year_tuples)>0:
			return self.custum_month_year_tuples
		else:




	def get_threads_from_file(self):
