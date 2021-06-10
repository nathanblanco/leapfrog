# code to simulate dependent condition of the Leapfrog task from Blanco et al. 2016
# and check the overall probability of jumps across trials 
# tested on python 2.7

# import some stuff (you'll need to install numpy if you don't have it)
from random import random
from numpy import *



means_list = []

# starting probability of a jump whenever it resets (i.e. after a previous jump)
starting_prob = 0.01

# amount that the probability increases on every trial that a jump does not occur
prob_increment = 0.01

# number of trials in the experiment
num_trials = 300

# number of simulations of the task to do
num_sims = 1000

# do a bunch of simulations of the task
for i in range(num_sims):

	# set the probability at the starting probability to start
	prob = starting_prob

	# make some lists to record current probability on each trial and whether or not a jump occurred
	probs_list = []
	jump_list = []

	# go through the trials of the task
	for i in range(num_trials):

		 # add the current probability of a jump to the list of probabilities for each trial
		 probs_list.append(prob)
	
		 # generate a random number used to check if a jump occurs on this trial
		 spinner = random.random()

		# determine if a jump would have occurred
		 if (spinner <= prob):
		 
			 # if so record it, and reset the jump probability
			 jump_list.append(1)
			 prob = starting_prob
		
		 else:
			 # if not, increase the probability of a jump
			 jump_list.append(0)
			 prob += prob_increment
	
	
	#print probs_list
	#print jump_list
	
	#print mean(probs_list)
	#print mean(jump_list)
	
	# add the proportion of trials that a jump occurred in this simulation to the list of all simulations
	means_list.append( mean(jump_list) )

# print the mean jump proportion (and its standard deviation) from all the simulations
print "Probability of a jump across "+str(num_sims)+" simulations: "+ str(mean(means_list))+"\n"
print "Standard deviation: "+str(std(means_list))
         