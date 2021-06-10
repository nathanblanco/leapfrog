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
        
    allsubjdata = []
    subj = 'x'
    subjindex = -1
    for line in alldata:
        if (line[0] != subj):
            subj = line[0]
            allsubjdata.append([line])
            subjindex += 1
        else:
            allsubjdata[subjindex].append(line)
            
    return allsubjdata

def getBIC(LL, num_params):
    return -2*LL + num_params*log(TRIALS_END-TRIALS_START)


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


def getModelLikelihood(exploit, subj_trials):

    
    neg_log_likelihood = 0.
    
    alpha = 1.
    Q = array([20.0, 10.0])

    for trial in range(NUM_TRIALS):
        trial_reward = float(subj_trials[trial][7])
        #choseExploit = int(subj_trials[trial][9])
        subj_action = int(subj_trials[trial][6])
        
        p_right = getActionProbability(array( [Q[0], Q[1]]), exploit)
        p_left = getActionProbability(array( [Q[1], Q[0]]), exploit)
        #print p_left, p_right, exploit
        #print Q, exploit


        if(TRIALS_START <= trial<  TRIALS_END ): neg_log_likelihood += log( [p_right,p_left][subj_action])

        Q[subj_action] += alpha * (trial_reward - Q[subj_action]) 


    return neg_log_likelihood



NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]


data = openfile("/Users/njb786/Desktop/LeapfrogPaper/data_analysis/all_subjects3.dat")

    
for subj in data:
    best_subj_ll = -inf
    for exploit in linspace(.01, .3, 51):
            ll = getModelLikelihood(exploit, subj) #subj
            if (ll > best_subj_ll): [best_exploit, best_subj_ll] = [exploit, ll]
    print subj[0][0], subj[0][1], best_subj_ll, getBIC(best_subj_ll, 1), best_exploit



