# fits subject data to the ideal actor and belief model
"""belief updates can be performed with only the past belief, 
    the last action, and the last observation, given knowledge
    of the observation and transition functions"""
    
from pylab import *
from numpy import *
from copy import copy
from scipy.stats import *
from scipy.optimize import fmin, brute
from string import split
from random import random, choice, uniform
import os
import sys
import cPickle
from time import time



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
    
def get_subj_likelihood(iparams, subjdata, beliefs_only=False, RL=False, full_output=False):
     
     #allStateActVals = loadAllStateActVals(NUM_TRIALS, load_cached=True)
     print iparams
     
     if iparams[0]<0.0 or iparams[0]>0.40:
         return 100000.0
     if iparams[1]<0.0:
         return 100000.0
     
     belief_p_flip = iparams[0] # p_flip as parameter
     #belief_p_flip = 0.075 # tied to actual p_flip
     SMtemp = iparams[1]
     
     subj = subjdata[0][0]
     rewards = []
     for line in subjdata:
        rewards.append([ float(line[4]), float(line[5]) ]) # makes a list of potential rewards for each trial
        
    
    ####### copied from doActorSim
     highestRawActionSeen = 0 # which action has the highest observed reward #B = 0, A = 1    
     highestRewardSeen = 20 #right?
     
     # pre/post mean before/after considering possible hidden jumps
     preJumpBelief = 1 # this is the belief after the last action and observation, but before a potential hidden jump; it should be used to get the following step's preJumpBelief (postJumpBelief should not be used)
     postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, belief_p_flip)) # get inital belief vector
     postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2] # belief that exploiting is optimal 

     # UNCOMMENT THIS PART FOR IA FITS
     state_act_val_p_flips = array(sorted(allStateActVals.keys()))
     state_act_val_p_flip = state_act_val_p_flips[(belief_p_flip <= state_act_val_p_flips)][0]
     trialStateActVals = allStateActVals[state_act_val_p_flip] # sets the StateActVals for that belief p_flip

    #num_jumps_seen = 0 # number of jumps seen this trial
     [a0, b0] = [belief_p_flip*10, (1-belief_p_flip)*10]  # initial values for each action
    #belief_p_flip = (num_jumps_seen+a0) / (num_jumps_seen+a0-num_jumps_seen+b0) # find this equation in paper # num_jumps_seen is 0 so a0/a0+b0

     if(full_output): model_trials = []
     
     model_choice_probs = [] # probability the model would make the choice the subject made

     for trial in range(NUM_TRIALS):
         
         
         if(beliefs_only):
             p_exploit = getActionProbability(array([postJumpBelief, 1.-postJumpBelief]), SMtemp) # get action probs based just on beliefs about whether flip or not
             p_explore = 1- p_exploit
         
         elif (RL):
             p_exploit = getActionProbability(array([1,0]), SMtemp)
             p_explore = 1- p_exploit

         else:
             stateActVals = trialStateActVals[((NUM_TRIALS-trial) * 2)- 1]['stateActVals'].copy() # list of 9 values for each in acts ? 
             acts  = trialStateActVals[((NUM_TRIALS-trial) * 2)- 1]['acts'].copy()  # 2 = ?, 1 = ?, 0 = ?
             extended_belief  = concatenate((postJump3StateBelief, zeros(6))) # # why is it extended?
             vals = inner(concatenate((postJump3StateBelief, (0,0,0,0,0,0))), stateActVals) # multiplies 3 state belief times by stateActVals for those states

             maxActVal = max(vals) # then pick the highest (highest posterior state?)
             maxValAct = acts[where(vals==max(vals))[0][0]] # action with the greatest value? what are 1 and 2?

             exploitOptimal = (maxValAct == 0) 
             suboptActionValue = getSuboptActVal(exploitOptimal, trialStateActVals, preJumpBelief, postJump3StateBelief, belief_p_flip, trial)
             
             p_opt = getActionProbability(array([maxActVal, suboptActionValue]), SMtemp)
             if (exploitOptimal):
                 p_exploit = p_opt
                 p_explore = 1 - p_opt
                            
             else:
                 p_explore = p_opt
                 p_exploit = 1 - p_opt
                 
         # record whether the subject exploited or explored # MAKE SURE THIS IS WORKING RIGHT
         subjchoice = int(subjdata[trial][6])

         if subjchoice == highestRawActionSeen:
             subj_exploit = 1 # exploit
             p_action_taken = p_exploit
    
         else:
             subj_exploit = 0 # explore
             p_action_taken = p_explore
             
         model_choice_probs.append(p_action_taken)
         
         trial_reward = float(subjdata[trial][7])

         jumpsObserved = 0  # jumps observed on this trial
         if(trial_reward > highestRewardSeen): # if one or more jumps have occurred
             jumpsObserved = (trial_reward - highestRewardSeen) / 10 
             highestRewardSeen = trial_reward
             highestRawActionSeen = subjchoice
         
         
         if(full_output):
             a_switch=  {True:1,False:0}[(trial!=0) and rewards[trial][0]!=rewards[trial-1][0]] # if a jumped
             b_switch= {True:1,False:0}[(trial!=0) and rewards[trial][1]!=rewards[trial-1][1]] # if b jumped
             model_trials.append( {'resp': subjchoice,  # choice made by subjcet
                '                   reward': trial_reward,  # reward for this trial
                                    'belief_before': postJumpBelief, # belief that exploiting is optimal
                                   'a_switch': a_switch,
                                   'b_switch': b_switch,
                                   'a_reward': rewards[trial][0],
                                   'b_reward': rewards[trial][1],
                                   'opt_resp': {True:1, False:0}[trial_reward == max(rewards[trial])],
                                   'jumps_observed':jumpsObserved,
                                   'explore':(subj_exploit==0), # did the subject explore
                                   'rel_val_exploit': {True: (maxActVal-suboptActionValue),
                                                       False: -1*(maxActVal-suboptActionValue)}[exploitOptimal],
                                   'rel_val_max_opt':maxActVal-suboptActionValue, 
                                   'belief_p_flip':belief_p_flip,
                                   'model_choice_prob': p_action_taken})
             
         preJumpBelief = getStateDistFromLastBelief(preJumpBelief, subj_exploit, jumpsObserved, belief_p_flip)[0] # updates preJumpBelief for next trial
         
          # these are used for action selection next trial
         postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, belief_p_flip))
         postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2]
         
     totalLoglikelihood = 0
     
     for i in model_choice_probs:
         totalLoglikelihood += log(i)

     if(full_output):  return subj, totalLoglikelihood, model_trials
     else:
        print totalLoglikelihood
        return -(totalLoglikelihood) # negative Log likelihood --to be minimized
    



def getActionProbability(orig_action_values, exploitation):
    if(orig_action_values[0] == orig_action_values[1]): action_values = array([1,1])
    elif(max(orig_action_values)==orig_action_values[0]): action_values = array([orig_action_values[0]-orig_action_values[1], 0])
    else: action_values = array([ 0, orig_action_values[1]-orig_action_values[0]])
    numerator = exp( action_values[0] * exploitation)
    denominator = sum( exp(action_values * exploitation) )
    if(isinf(numerator) or isinf(denominator)):
        print action_values
        raise SystemExit, 'exp() blew up'
    return numerator / denominator


def loadAllStateActVals(num_trials, load_cached=False):
    if(load_cached):
        filename = 'cached_alphas/'+str(num_trials)+'_trial_state_act_vals.dat'
        print 'loading alpha files from:', filename
        temp = open(filename, 'rb')
        allStateActVals = cPickle.load(temp)
        temp.close()
        return allStateActVals
    else:
        print 'loading alpha files from alpha directory'
        allStateActVals = {}
        alpha_dirs = filter(lambda x:(str((2*num_trials)-1)+'_trial' in x),  os.listdir('alphas/'))
        alpha_p_flips = array(sorted(map(lambda x:float(x.split('_')[3]),alpha_dirs)))
        for alpha_p_flip in alpha_p_flips:
            stateActValsGivenTrial = {}                 
            dir_name = './alphas/alphas_'+str((2*num_trials)-1)+'_trial_'+str(alpha_p_flip)
            print '\t', dir_name
            file_names = os.listdir(dir_name)
            for file_name in file_names:
                if(not ('.alpha' in file_name)): continue
                if(file_name.split('alpha')[1]==''): continue
                alpha_file = file(dir_name+'/'+ file_name, 'r')
                horizon = int(file_name.split('alpha')[1])
                alpha_lines = alpha_file.readlines()
                alpha_file.close()
                alpha_array = filter(lambda x:len(x) > 1, alpha_lines)
                acts = filter(lambda x:len(x) == 2, alpha_array)
                acts = map(lambda x:float(x[0]), acts)
                acts = array(acts)
                stateActVals = filter(lambda x:len(x) > 3, alpha_array)
                stateActVals = map(lambda x:split(x, ' '), stateActVals)
                stateActVals = map(lambda x:x[0:9], stateActVals)
                stateActVals = array(map(lambda x:map(float, x), stateActVals))
                stateActValsGivenTrial[horizon] = {'acts':acts, 'stateActVals':stateActVals}
            allStateActVals[alpha_p_flip] = stateActValsGivenTrial
        filename = 'cached_alphas/'+str(num_trials)+'_trial_state_act_vals.dat'
        print 'saving cached alpha files to:', filename
        temp = open(filename, 'wb')
        cPickle.dump(allStateActVals, temp, True)
        temp.close() 
    return allStateActVals


def recomputeBelief(model_trials, post_vol):
    preJumpBelief = 1
    for trial in model_trials:
        preJumpBelief = getStateDistFromLastBelief(preJumpBelief, 1-trial['explore'], trial['jumps_observed'], 
                                                   post_vol)[0]
    return preJumpBelief


def getSuboptActVal(exploitOptAct, trialStateActVals, preJumpBelief, postJump3StateBelief, belief_p_flip, trial):
     if(exploitOptAct): # assumes that the actor will explore, since this is the suboptimal action
          exploit = 0
          obsByUnobsJumps = array([0, 1, 1]) # ?
          relRewByUnobsJumps = array([0, 10, 0]) # ?
          immedRew = inner(postJump3StateBelief, relRewByUnobsJumps)  #if the suboptimal action is to explore
     else: # suboptimal action is exploit
          exploit = 1
          obsByUnobsJumps = array([0, 0, 2]) # ?
          relRewByUnobsJumps = array([10, 0, 10]) # ?
          immedRew = inner(postJump3StateBelief, relRewByUnobsJumps)  #if the suboptimal action is to exploit

     suboptActionValue = immedRew
     nextTrialAlphaIndex = ((NUM_TRIALS-(trial+1)) * 2) - 1 # *2 - 1 again
     if nextTrialAlphaIndex > 0:
         for hypothUnobservedJumps in range(0,3):
             obsJumps = obsByUnobsJumps[hypothUnobservedJumps]
             hypothPreJumpBelief = getStateDistFromLastBelief(preJumpBelief, exploit, obsJumps, belief_p_flip)[0]
             if isnan(hypothPreJumpBelief):  continue
             hypothPostJump3StateBelief = array(get3StateDistFromPreJumpDist(hypothPreJumpBelief, belief_p_flip))
             hypothStateActVals = trialStateActVals[nextTrialAlphaIndex]['stateActVals'].copy()
             hypothActs  =trialStateActVals[nextTrialAlphaIndex]['acts'].copy()

             hypothMaxAct = None
             hypothMaxVal = 0
             extended_belief  = concatenate((hypothPostJump3StateBelief, zeros(6)))

             hypothVals = inner(concatenate((hypothPostJump3StateBelief,(0,0,0,0,0,0))), hypothStateActVals)
             hypothMaxVal = max(hypothVals)
             hypothMaxValAct = hypothActs[ where(hypothVals==max(hypothVals))[0][0] ]

             suboptActionValue += postJump3StateBelief[hypothUnobservedJumps] * hypothMaxVal
     return suboptActionValue
    

###   
# Guide to arguments:                                
# 1) lastBelief - the prob that exploit (as defined after the second-to-last action and observation)
# gave the highest reward before the last action and observation.
# 2) exploit - whether the last action was an exploit (vs. explore)
# 3) jumpsObserved - how many previously unobserved jumps were observed in the last observation.
# 4) jumpProb - the preset volatility rate               
#                                                                                           
# This function returns the probability that, after the last action and observation but before the
# potential next jump, exploiting will receive the highest reward. The first number returned is this
# probability in terms of what action is considered the exploit action after the last observation,
# and the second number is in terms of the action that was exploitative before the last observation
# (i.e., the action that lastBelief considers exploitative).
###
def getStateDistFromLastBelief(lastPreJumpBelief, exploit, jumpsObserved, jumpProb):
    if exploit:        obsByNumJumps = array([0, 0, 2] )
    else:         obsByNumJumps = array([0, 1, 1])
    jProb00 = lastPreJumpBelief * (1 - jumpProb) * (jumpsObserved == obsByNumJumps[0])
    jProb01 = lastPreJumpBelief * jumpProb * (jumpsObserved == obsByNumJumps[1])
    jProb11 = (1 - lastPreJumpBelief) * (1 - jumpProb) * (jumpsObserved == obsByNumJumps[1])
    jProb12 = (1 - lastPreJumpBelief) * jumpProb * (jumpsObserved == obsByNumJumps[2])
    probPrevExploitOptNum = jProb00 + jProb12
    probPrevExploitOptDen = probPrevExploitOptNum + jProb01 + jProb11
    probPrevExploitOpt = probPrevExploitOptNum / probPrevExploitOptDen
    probCurrExploitOpt = probPrevExploitOpt
    if not exploit and jumpsObserved == 1:        probCurrExploitOpt = 1 - probCurrExploitOpt
    return (probCurrExploitOpt, probPrevExploitOpt)

###
# This function should be called to convert the output of getStateDistFromLastBelief()
# to the three-state belief state used in the POMDP specification, which includes 
# consideration of the a possible post-observation jump.

###
def get3StateDistFromPreJumpDist(belief, jumpProb):
    noJumpProb = 1 - jumpProb
    twoStateDist = (belief, 1- belief)
    postJumpState1Prob = twoStateDist[0] * noJumpProb
    postJumpState2Prob = (twoStateDist[0] * jumpProb) + (twoStateDist[1] * noJumpProb)
    postJumpState3Prob = twoStateDist[1] * jumpProb
    return (postJumpState1Prob, postJumpState2Prob, postJumpState3Prob)


#####################
def overall_fit(data, iparams, evalf):
    #print "starting brute force grid search"
    roughsearch = brute(evalf, [[0.01,0.38],[0.001,7.0]],data,Ns=28,full_output=1)
    print "starting fine-grained search"
    # then do a finer Nelder-Mead search in the local area
    res = fmin(evalf, roughsearch[0], data,full_output=1) #roughsearch[0]
    #res = fmin(evalf, iparams, data, maxfun=1000, maxiter=5000, full_output=1)
    print res
    return res

    
def do_subj_fit(subjdata):
    
    
    f=open("/Users/njb786/Desktop/LeapfrogPaper/data_analysis/fits/IASubFits/%s.dat" % (subjdata[0][0]),"w+")
    
    fit = 100
    tries = 0
    while fit > 0.05:
        print "Fitting"
        iparams = [uniform(0.0,0.25), uniform(0.00,4.0)]
        #print iparams # belief_p_flip, SMtemp
        res = overall_fit([subjdata], iparams, get_subj_likelihood)
       
        f.write(str(subjdata[0][0])+' '+str(subjdata[0][1]+' '+str(res[0][0]))+' '+str(res[0][1])+' '+str(res[1]))
        f.write('\n')
        f.flush()
        fit=res[1]
        tries+=1
        if tries>0:
            break



NUM_TRIALS = 300
#NUM_TASKS = 1 # 0 means single task data, 1 means dual task data

# the parameters that should be fit
#belief_p_flip = .075
#SMtemp = 0.38
#iparams = [0.075, 0.38]

global allStateActVals 
allStateActVals= loadAllStateActVals(NUM_TRIALS, load_cached=True)

data = openfile("/Users/njb786/Desktop/LeapfrogPaper/data_analysis/all_subjects.dat") 
do_subj_fit(data[int(sys.argv[1])])





