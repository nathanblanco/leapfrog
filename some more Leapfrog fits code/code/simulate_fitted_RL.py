from pylab import *
from numpy import *
from copy import copy
from scipy.stats import *
from string import split
from random import random, choice
import os
import cPickle, pickle


def openfile(filename):
    myfile = open(filename)
    alldata = myfile.readlines()
    
    for i in range(len(alldata)):
        alldata[i]=alldata[i].split()
      
    return alldata

def getBIC(LL, num_params):
    return -2*LL + num_params*log(TRIALS_END-TRIALS_START)

def generateLeapfrogRewards(num_trials, p_flip):
     leapfrog_rewards = zeros((num_trials,2))
     a_reward = 10
     b_reward = 20
     last_changed = 'b'
     num_switches = 0
     for trial_num in range(num_trials):
          if(random() < p_flip):
               num_switches += 1
               if(last_changed == 'b'): 
                    last_changed  = 'a'
                    a_reward += 20.0
               else:
                    last_changed = 'b'
                    b_reward += 20.0
          leapfrog_rewards[trial_num] = array([b_reward,a_reward])
     return [array(leapfrog_rewards), num_switches / float(num_trials)]

def recomputeBelief(model_trials, post_vol):
    preJumpBelief = 1
    for trial in model_trials:
        preJumpBelief = getStateDistFromLastBelief(preJumpBelief, 1-trial['explore'], trial['jumps_observed'], 
                                                   post_vol)[0]
    return preJumpBelief

def getProbabilisticAction(resp_prob):
    rand_num = random()
    if(rand_num <= resp_prob):  return 1
    else:   return 0

def getActionProbability(action_values, exploitation): # orig_action_values
    #print orig_action_values
    #if(orig_action_values[0] == orig_action_values[1]): action_values = array([1, 1])
        
    #elif(max(orig_action_values)==orig_action_values[0]): action_values = array([1, 0])
    #else: action_values = array([ 0, 1])
        
    numerator = exp( action_values[0] * exploitation) # action_values
    denominator = sum( exp( action_values * exploitation) ) #action_values
    if(isinf(numerator) or isinf(denominator)):
        print action_values
        raise SystemExit, 'exp() blew up'
    return numerator / denominator

def doModelSimTrials(subj, cesd, exploit, sim_trials, debug = False):
    
    highestRawActionSeen = 0 #B, right?    
    highestRewardSeen = 20 #right?
    
    neg_log_likelihood = 0.
    
    model_trials = []
    
    alpha = 1.
    Q = array([20.0, 10.0])

    for trial in range(NUM_TRIALS):
    
        
        p_right = getActionProbability(array( [Q[0], Q[1]]), exploit)
        p_left = getActionProbability(array( [Q[1], Q[0]]), exploit)
        #print p_left, p_right, exploit
        #print Q, exploit

        action = getProbabilisticAction(p_left)
        trial_reward = sim_trials[0][trial][action]

        if action == highestRawActionSeen:
            choseExploit = 1
        else:
            choseExploit = 0

        trial_reward = sim_trials[0][trial][action]
        isBest = (trial_reward == max(sim_trials[0][trial]))
        explore_opt = 'x'
        
        if(trial_reward > highestRewardSeen):
            highestRewardSeen = trial_reward
            highestRawActionSeen = action

        model_trials.append([subj, cesd, trial+1, sim_trials[0][trial][0], sim_trials[0][trial][1], action, choseExploit, int(isBest), explore_opt])

        if debug == True:
            print 'Rewards: %s' % sim_trials[0][trial]
            print 'Action: %s' % action
            print 'Exploit? %s' % choseExploit
            print 'Best?  %s' % isBest
            print 'prob left (ie. action == 1),  %s' % p_left

        
        Q[action] += alpha * (trial_reward - Q[action]) 


    return model_trials

def simulate_trials(num_sims, fit_data, num_trials, pflip):

	for i in range(num_sims):

		file = open("/Users/njb786/Dropbox/School/current_projects/Leapfrog/DepressionPaper/data_analysis/fits/RL_fitted_sims/RL_fitted_sim_trials-%s.txt" % (i+1), "w+")
		file.write("subj cesd trial b_reward a_reward action choseExploit isBest explore_opt \n")
	
		for line in range(len(fit_data)):
			sim_trials = generateLeapfrogRewards(num_trials, p_flip)
		
			#print fit_data[line]
		
			subj = fit_data[line][0]
			cesd = fit_data[line][1]
			exploit = float(fit_data[line][4])
		
			#subj_trials = getModelSimTrials(subj, cesd, exploit, belief_p_flip, trialStateActVals, sim_trials)
			subj_trials = doModelSimTrials(subj, cesd, exploit, sim_trials)
		
			for line in subj_trials:
				for datum in line:
					file.write(str(datum)+' ')
				file.write('\n')
				file.flush()


NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]
p_flip = 0.075



fit_data = openfile("/Users/njb786/Dropbox/School/current_projects/Leapfrog/DepressionPaper/data_analysis/fits/RLfits.txt")

num_sims = 100

simulate_trials(num_sims, fit_data, NUM_TRIALS, p_flip)



