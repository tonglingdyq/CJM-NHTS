import func, utils, time
import os, pathlib, ast, collections, sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# File names - Input
dataFileNameList = []
dataFileNameList.append('Bayesian_Clustering_Results_complete.xlsx')
dataFileNameList.append('Bayesian_Clustering_Results_dev3k.xlsx') 
dataFileNameList.append('Bayesian_Clustering_Results_dev200.xlsx')
# dataFileNameList.append('Bayesian_Clustering_Results_fulllength.xlsx')
dataFileNameList.append('Bayesian_Clustering_Results_uniform.xlsx')

# Settings of plot - Input
resultFolderPath = str(pathlib.Path(os.getcwd()).parent)+'/Results/Bayesian/' #Result folder path
rawFileName = 'Bayesian_Clustering_Results_0raw.xlsx' #File that contains unprocessed results
s = 21 #Number of states
threshold = 0.3 #Threshold of trans prob to be kept
plot_type = int(input('Please give the plot type (1 for heatmap (default), 2 for homogeneous, 3 for simulation-line, 4 for simulation-bar-random, 5 for simulation-bar-absorb, 6 for chord diagram): ') or 1)
if plot_type == 1:
	plot_type = 'heatmap'
elif plot_type ==2:
	plot_type = 'homogeneous'
elif plot_type ==3:
	plot_type = 'simulation-line'
elif plot_type ==4:
	plot_type = 'simulation-bar-random'
elif plot_type == 5:
	plot_type = 'simulation-bar-absorb'
elif plot_type ==6:
	plot_type = 'chord'
else:
	raise Exception('No such plot type!!!')
# plot_type = 'simulation-bar' #Plot type: 'heatmap', 'step', 'homogeneous', 'simulation-line', 'simulation-bar'
fig_type = 'multiple' #Figure type: 'single', 'multiple'
save_pdf = True #If saving all figures in a PDF
# print(resultFolderPath+resultFileAffix+'/')
########################### End of Inputs ####################################
resultPriorLs = [i.split('_')[-1].split('.xlsx')[0] for i in dataFileNameList] #List of prior type, will be used for output folder name
baselineFilePath =  resultFolderPath+rawFileName #Get the baseline file path
baselineFile = pd.ExcelFile(baselineFilePath) #Read the baseline file as an object
LabelT = baselineFile.parse('WindowLabels', header = None, index_col = 0) #Get the sheet baseline file that contains all the window labels (for plotting)
##########################################################################################
print('Current plot_type is [' + plot_type +']\nCurrent fig_type is ['+fig_type+']')
for fileNo, dataFileName in enumerate(dataFileNameList): #Loop over each file
	print('***********************************************************************************************')
	print('Loop starts for file: ',dataFileName.split('.xlsx')[0])
	##################
	last_time = time.time()
	##################
	resultPrior = resultPriorLs[fileNo]
	titles_dict = collections.defaultdict(list) #Create an empty dictionary for titles
	##################
	dataFilePath = resultFolderPath +dataFileName
	GeneralT = pd.read_excel(dataFilePath, sheet_name = 0,header = None) #Read the excel as a df
	GeneralT = GeneralT[GeneralT[2]!= '[]'] #Remove rows with no meaingful result
	GeneralT[2] = GeneralT[2].apply(ast.literal_eval) #Convert result col 2 to lists from str
	GeneralT[1] = GeneralT[1].apply(ast.literal_eval) #Convert result col 1 to lists from str
	GeneralT[1] = GeneralT[1].apply(lambda x: [a for a in x if a!= 1]) #Keeps only the # of meaningful clusters (remove all cluster#=1)
	GeneralT[0] = GeneralT[0].apply(lambda x: int(x.replace(' transitions:',''))) #Remove extra text from the transition no
	GeneralT = GeneralT.set_index(keys=0) #Use the 1st col as the index (1st col is # of transitions)
	# resultDict = GeneralT.drop(labels = 1,axis = 1).T.to_dict('list', into = collections.defaultdict(list)) #Create a dictionary where keys are the transition no, vals are the meaningful time window indices for that transition no
	resultNo = list(GeneralT.index) #List of all transitional no with meaningful result

	# We will mix the clustered result with baseline result, i.e. fill time windows without meaningful clusters/MCs with baseline cluster (a single cluster)
	# processedFilePath = func.processed_data_generator(dataFilePath, baselineFilePath, resultNo, func_type = 'Read') #Get the processed file path
	
	##########################################################################################
	# resultNo = [2] #Test case
	for transitionNo in resultNo: #Loop over each transition number/sheet
		# Read background info for this transition number from baseline file
		sheet_name = str(transitionNo) +' Transition'
		baselineT = baselineFile.parse(sheet_name = sheet_name, header = None)
		mc_num_ls = ast.literal_eval(baselineT.iloc[0,1]) #Get the list of number of MCs for each time window
		windowLabels = LabelT.loc[sheet_name, ~LabelT.loc[sheet_name].isnull()].tolist() #Extract the window labels for current transition number
		print('Current transition number is',transitionNo)
		# Individual sheet analysis
		titles_dict['title_sheet'] = str(transitionNo)+' transitions' #Assign the titles for the entire sheet
		SpecificT = pd.read_excel(dataFilePath, sheet_name = sheet_name, header = None) #Read the excel sheet for current transitional #
		
		dataT = SpecificT[(~SpecificT[0].isnull()) & ((SpecificT[0].apply(type) == float) | (SpecificT[0].apply(type)== int))] #Extract all the meaningful time window data (trans mat) in a single df
		windowArray = GeneralT.loc[transitionNo, 2] #Get the list of meaningful time window indices (which time windows within the current transitional # have meaningful results), this index is 1-indexed
		transCountArr = GeneralT.loc[transitionNo, 1] #Get # of transitional mat for each time window in a list
		rowRangeArr = utils.calcRow(windowArray,s, ttype = 'Result') #Get the rows in sheet where those time windows are located
		mc_sheet = collections.defaultdict(list) #Create an empty dictionary that will save corresponding MC data for this excel sheet
		
		##########################################################################################
		titles_dict['title_win'] = [] #Reset titles_dict's title_win list for current sheet
		for idx, windowIdx in enumerate(windowArray): #Iterate over different time windows that have meaningful results
			windowData = dataT.iloc[(idx*s):(idx+1)*s,:] #Crop out all the data for this time window (idx is window # for this transition #)
			transCount = transCountArr[idx] #Num of trans mat for this time window
			# Create empty list for both mc_data and pmat
			mc_window = []
			pmat_window = []
			# Create title for this time window
			title_idx = rowRangeArr[idx][0]-1 #Row number of the title for the current window in SpecificT
			title_row = SpecificT.iloc[title_idx,:][SpecificT.iloc[title_idx,:].notnull()] #Get the row for the title
			window_title = title_row.iloc[1].split(' - ')[0]+' - '+title_row.iloc[-1].split(' - ')[1] #Get the window title
			titles_dict['title_win'].append(' Window No. '+str(windowIdx)+': '+window_title) #Assign the titles for a time window (for plot_type plotting)
			# Iterating over each MC within the window and plot it
			for chainNo in range(transCount): #Iterate over each Markov chain
				pmat = windowData.iloc[:,chainNo*(s+1):chainNo*(s+1)+s] #Transitional matrix for current MC
				pmat_window.append(pmat) #Append raw pmat to list (not the one after threshold)
				state_valid = utils.node_validate(pmat.to_numpy()) #Valid state within this MC
				pmat_threshold = pmat[pmat>threshold].fillna(0) #Only the nodes above threshold will count
				################ Commented: See below for details
				# # The following code checks if the pmat would transit to a null state which has 0 trans prob to any states
				# node_valid = utils.node_validate(pmat, start_num = 0) #Get all the valid nodes (0-indexed)
				# for node in node_valid: 
				# 	transprob = pmat.to_numpy()[node]
				# 	if 1 - sum(transprob) > 0.01:
				# 		print('Window idx is',idx, 'chainNo is',chainNo, 'node is',node+1 ,'sum is',sum(transprob))
				################
				# Depends on the plot type, we will use different forms of data
				if plot_type == 'step' or plot_type == 'homogeneous':
					# If plot type is 'step' or 'homogeneous', we will use mc_dict keyed by edge tuple pairs and valued by trans prob
					# 'step': Treat end of edges as the next state by modifying the end states to a different set of indices (same labels still)
					# 'homogeneous': Use original states
					mc_dict = func.pmat2dict(pmat_threshold,plot_type) #Convert pmat to a dict 
					mc_window.append(mc_dict) #Append to the window
				elif plot_type == 'heatmap': 
					# If plot type is 'heatmap', we will use the transitional matrix directly
					mc_window.append(pmat)
				elif plot_type.startswith('simulation') or plot_type == 'chord':
					mc_window.append(pmat) #Use original pmat for simulation (not the threshold one) and chord graph
				else: #Simulation type plot has pmat already appended
					raise Exception('There is no such plot type!')
			# Note:Both entries of mc_sheet are lists, and each entry is either a mc_window or a pmat_winodw
			mc_sheet['mc_data'].append(mc_window) #Append mc_window to the list
			mc_sheet['pmat'].append(pmat_window) #Append pmat_window to the list
		##########################################################################################
		# Plot everything from this excel sheet 
		# First plot out the number of meaningful clusters and number of MCs in the window vs the time window
		fig_transCount, ax_transCount0 = plt.subplots(num = -1, figsize = [15,10], tight_layout = True,
			subplot_kw= {'xlabel': 'Time Windows', 'ylabel': 'Number of Meaningful Clusters Generated'})  #-2 for translation table, -1 for meaningful clusters
		axis_kw = {'tick_label_size': 13, 'axis_label_size': 20, 'fontdict': {'size': 10,'weight': 'bold'}, 'legend_text_size': 15, 'suptitle_size': 25}
		fig_transCount.suptitle('Number of Clusters and Markov Chains in Time Windows of '+sheet_name, size=axis_kw['suptitle_size']) #Create the figure
		plt0 = ax_transCount0.bar(windowArray, transCountArr, label = 'Number of Meaningful Clusters')  #Plot number of generated clusters for each meaningful window
		rects = ax_transCount0.patches #Get the rectangles(bars) in the plot
		for rect_i, rect in enumerate(rects):
			ax_transCount0.text(rect.get_x() + rect.get_width() / 2, rect.get_height()+0.01, transCount, ha='center', va='bottom', fontdict = axis_kw['fontdict']) #Place a label on top of the bar
		ax_transCount1 = ax_transCount0.twinx() #Instance a second axes that shares the same x-axis
		plt1 = ax_transCount1.plot(range(1,len(windowLabels)+1), mc_num_ls, 'ro-', label = 'Number of MCs in Time Window') #Plot number of MCs in the window
		ax_transCount0.legend([plt0, plt1[0]],[plt0.get_label(),plt1[0].get_label()], fontsize = axis_kw['legend_text_size'])
		
		# Axis properties
		ax_transCount0.set_ylim(0,10)
		ax_transCount0.set_xlim(0,48)
		ax_transCount0.tick_params(axis = 'x',which = 'major' ,bottom = False, labelbottom = True, labelsize = axis_kw['tick_label_size']) #Turn off x-axis major ticks & labels
		ax_transCount0.set_xticks(range(1,len(windowLabels)+1)) #Set x-axis minor ticks
		ax_transCount0.set_xticklabels(labels = windowLabels, rotation = 'vertical') #Set xtick labels and orientation
		ax_transCount0.xaxis.label.set_size(axis_kw['axis_label_size']) #Set size of axis label size
		ax_transCount0.yaxis.label.set_size(axis_kw['axis_label_size']) #Set size of axis label size
		ax_transCount1.set_ylim(0,500)
		ax_transCount1.set_ylabel('Number of Markov Chains in Time Window', size = axis_kw['axis_label_size'])
		######################################
		# Plot the specific plot type given by the user
		func.plot_mc_sheet(mc_sheet['mc_data'],titles_dict, transCountArr, plot_type = plot_type, fig_type = fig_type,save_pdf = save_pdf, 
			resultFolderPath = resultFolderPath+resultPrior+'/', suffix = resultPrior, prefix = plot_type,#This line deals with input for func.plot_mc_sheet
			fig_kw = {'fig_size': (15,10), 'constrained_layout': False, 'tight_layout': True, 
			'ax_kw':{'aspect': 'auto'},
			'suptitle_kw':{'size': 15}}, #fig generator settings (ax_kw, kwargs for axes; suptitle_kw, kwargs for figure suptitle)
			plot_kw = {'colormap': 'hsv', 'font': {'fontsize': 11}} #plot_mc settings
			)
		##########################################################################################
		# # Simulate all the MCs on this excel sheet - Currently undeveloped
		# func.simulate_mc_sheet(mc_sheet['pmat'], n_steps = 20000, initial_state = 0, **kwargs)

	print('Time spent on this dataFile is',time.time() - last_time)
##########################################################################################
