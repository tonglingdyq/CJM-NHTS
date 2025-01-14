import numpy as np
import pandas as pd
from math import *
import func, collections, utils, importlib, ujson


###################### Test #######################
f = open('output/dist_dict0.json','r')
dist_dict0 = ujson.loads(f.read())
dist_dict0 = func.dict_key2tuple(dist_dict0)
###################### Test #######################
file_trip  ='/Users/yichingding/Google Drive/School/Stanford/Research/IRIS/Journey Map/Markov Chain Paper/Code & Data/Data/trippub_top2k.csv'
trip_ls  = func.data_processing(file_trip) #Generate the day trips for dataset
#Generate initial population (a set of CJMs each as an individual)
m = 10 # Maximum length of CJs in initial ppl CJMs (also determines the number of ini ppl CJMs = m-1)
n = 5 # Number of CJs in initial ppl CJMs
gen_max = 300 #Number of generations
ppl, top_n = func.ini_ppl_gen(trip_ls, m, n) #Generate the initial populations
###################### New #######################
center_dict_all = {} #Create an empty dictionary for assignment
cjm_score = collections.defaultdict(list)
record = [['Key','Best CJM','Score']] #List of [best CJM key, current best CJM, current best score]
func.save_ls2csv(record, writetype = 'w' , filename='output/FinalResult.csv')

for t in range(gen_max):
	#Assign CJs to current ppl and evaluate current population (CJMs)
	for key, center_ls in ppl.items(): #key is identifier in [2, top_num], center_ls is a CJM (a list of centers/CJs in the CJM)
		#Note that for initial ppl, key is length of individual journey (i in CJM_i).
		dist_dict1 = utils.cal_cross_dist(trip_ls, center_ls, dist_dict0) #Compute the distances between all trips and current centers given dist_dict0
		center_dict_all[key] = func.cjm_assign(trip_ls, center_ls, dist_dict1) #Assign each journey to the closest centers/cluster in CJM_i (returns a dictionary)
		score = func.cjm_eval(trip_ls, center_ls, center_dict_all[key], dist_dict1) #Compute score for the current CJM
		cjm_score[key].append(score) #Saves the score for current CJM and generation (each cjm_score[key] is a list of scores of history)
	cjm_sort_ls = sorted(cjm_score, key = lambda x: cjm_score[x][-1], reverse = 1) #Sort the CJM by their latest score in descending order
	print('The best CJM at time ' + str(t) + ' is CJM #' + str(cjm_sort_ls[0]) +' and its score is '+ str(cjm_score[cjm_sort_ls[0]][t]))
	#Saves [key, current best CJM, current best score] to a list
	record = [str(cjm_sort_ls[0]), str(ppl[cjm_sort_ls[0]]), str(cjm_score[cjm_sort_ls[0]][t])]
	func.save_ls2csv(record, writetype = 'a' , filename='output/FinalResult.csv')
	ppl = func.ga_CJM(ppl, cjm_score, top_n) #Genetic operations

# Final evaluation
for key, center_ls in ppl.items(): #center_ls is a CJM (a list of centers/CJs in the CJM), key is identifier in [2, top_num]
	dist_dict1 = utils.cal_cross_dist(trip_ls, center_ls, dist_dict0) #Compute the distances between all trips and current centers
	center_dict_all[key] = func.cjm_assign(trip_ls, center_ls, dist_dict1) #Assign each journey to the closest centers/cluster in CJM_i
	score = func.cjm_eval(trip_ls, center_ls, center_dict_all[key], dist_dict1) #Compute score for the current CJM
	cjm_score[key].append(score)
cjm_sort_ls = sorted(cjm_score, key = lambda x: cjm_score[x][-1], reverse = 1) #Sort the CJM by their latest score in descending order
print('The best CJM at time ' + str(t) + ' is CJM #' + str(cjm_sort_ls[0]) +' and its score is '+ str(cjm_score[cjm_sort_ls[0]][t]))
record = [str(cjm_sort_ls[0]), str(ppl[cjm_sort_ls[0]]), str(cjm_score[cjm_sort_ls[0]][t])]
func.save_ls2csv(record, writetype = 'a' , filename='output/FinalResult.csv')
print('The final CJM is #'+ str(cjm_sort_ls[0]) +': '+str(ppl[cjm_sort_ls[0]]))

###################### Test #######################

# importlib.reload(func)
# importlib.reload(utils)
# print('the current map is ' + str(key) + ' and assignment is completed')