# --------------------------------------------------------------
#  Ideal Actor model:
# -This code fits the Ideal Actor model to Leapfrog task data.
#  This model explores more often when uncertainty is greater.
#  We fit it with two free parameters. The p(flip) parameter
#  represents the belief in how often the flips in reward value
#  happen in the task. 'exploit' is the Softmax inverse temperature
#  parameter. When the p(flip) is set at the true flip value and with 
#  deterministic responses (i.e. inverse temp = infinity) the model
#  makes the optimal choice on every trial.
# --------------------------------------------------------------

# import some modules
from pylab import *
from numpy import *
from copy import copy
from scipy.stats import *
from string import split
from random import random, choice
import os
import cPickle, pickle

# this function opens a datafile containing data from all subjects.
# It divides it each subject into a separate list, within which each
# line/trial is a list containing the data for that trial
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

# computes the BIC value from the negative log likelihood and the number of parameters
def getBIC(nLL, num_params):
    return 2*nLL + num_params*log(TRIALS_END-TRIALS_START)


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

# softmax action selection on the action values 
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

# the values for each action at each trial, given the
# current belief-state (i.e. probability of an unseen flip), are computed
# by formulating the task as a POMDP and using pomdp-solve. Run the 
# 'generate_alphas_from_p_flip.py' file before fitting this model for the first time.
# The values will be stored in the 'alphas' folder. The first time you run this, set
# 'load_cached=False' where it is called below. This function will load the values, 
# as well as cache them in a single file for use later.
# Later you can set 'load_cached=True', and it will save time.
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

def getSuboptActVal(exploitOptAct, trialStateActVals, preJumpBelief, postJump3StateBelief, belief_p_flip, trial):
     if(exploitOptAct): # assumes that the actor will explore, since this is the suboptimal action
          exploit = 0
          obsByUnobsJumps = array([0, 1, 1])
          relRewByUnobsJumps = array([0, 10, 0])
          immedRew = inner(postJump3StateBelief, relRewByUnobsJumps)  #if the suboptimal action is to explore
     else: # suboptimal action is exploit
          exploit = 1
          obsByUnobsJumps = array([0, 0, 2])
          relRewByUnobsJumps = array([10, 0, 10])
          immedRew = inner(postJump3StateBelief, relRewByUnobsJumps)  #if the suboptimal action is to exploit

     suboptActionValue = immedRew
     nextTrialAlphaIndex = ((NUM_TRIALS-(trial+1)) * 2) - 1
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

def getStateDistFromLastBelief(lastPreJumpBelief, exploit, jumpsObserved, jumpProb):
    if exploit:    obsByNumJumps = array([0, 0, 2] )
    else: obsByNumJumps = array([0, 1, 1])
    jProb00 = lastPreJumpBelief * (1 - jumpProb) * (jumpsObserved == obsByNumJumps[0])
    jProb01 = lastPreJumpBelief * jumpProb * (jumpsObserved == obsByNumJumps[1])
    jProb11 = (1 - lastPreJumpBelief) * (1 - jumpProb) * (jumpsObserved == obsByNumJumps[1])
    jProb12 = (1 - lastPreJumpBelief) * jumpProb * (jumpsObserved == obsByNumJumps[2])
    probPrevExploitOptNum = jProb00 + jProb12
    probPrevExploitOptDen = probPrevExploitOptNum + jProb01 + jProb11
    probPrevExploitOpt = probPrevExploitOptNum / probPrevExploitOptDen
    probCurrExploitOpt = probPrevExploitOpt
    if not exploit and jumpsObserved == 1:    probCurrExploitOpt = 1 - probCurrExploitOpt
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


# helper function that sets things up for 'getModelLikelihood'
def getSoftmaxActorLikelihood(params, subj_trials, exploit):
#    [belief_p_flip, exploit] = params
#    [exploit] = params
    [belief_p_flip] = params
    belief_p_flip = round(belief_p_flip, 4)
    if((not (0 < belief_p_flip < .21)) or (not (0 < exploit < 10))): return 10000
    alpha_p_flips = array(sorted(ALL_STATE_ACT_VALS.keys()))
    try: alpha_p_flip = alpha_p_flips[alpha_p_flips <= belief_p_flip][-1]
    except: return [10000, 0, 0, 0, 0]
        #print ALL_STATE_ACT_VALS[alpha_p_flip]
    return getModelLikelihood(exploit, alpha_p_flip, ALL_STATE_ACT_VALS[alpha_p_flip], subj_trials)

# computes the negative log likelihood for the model given a participant's data and a set of parameters
def getModelLikelihood(exploit, belief_p_flip, trialStateActVals, subj_trials, beliefs_only=False, learn_p_flip=False, full_output=False):
    
    highestRawActionSeen = 0 #B  (option B, the one on the right)
    highestRewardSeen = 20 #


    num_jumps_seen = 0
    [a0, b0] = [belief_p_flip*10, (1-belief_p_flip)*10] #weak prior
    post_vol = (num_jumps_seen+a0) / (num_jumps_seen+a0-num_jumps_seen+b0)

    preJumpBelief = 1 # this is the belief after the last action and observation, but before a potential hidden jump; it should be used to get the following step's preJumpBelief (postJumpBelief should not be used)
    postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, belief_p_flip))
    postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2] # 
    
    if(full_output): model_trials = []
    else: [explore, opt_res] = [zeros(NUM_TRIALS), zeros(NUM_TRIALS)]
    
    log_likelihood = 0.
    Q = array([0.0, 0.0])

    for trial in range(NUM_TRIALS):
    
        # set beliefs_only = True to fit the 'Belief model' from Knox et al. 2012
        if(beliefs_only): # SOFTMAX ON BELIEFS
            p_exploit = getActionProbability(array([postJumpBelief, 1.-postJumpBelief]), exploit)
            
        else:  #SOFTMAX ON VALUES
            stateActVals = trialStateActVals[((NUM_TRIALS-trial) * 2)- 1]['stateActVals'].copy()
            acts  =trialStateActVals[((NUM_TRIALS-trial) * 2)- 1]['acts'].copy()
            extended_belief  = concatenate((postJump3StateBelief, zeros(6)))
            vals = inner(concatenate((postJump3StateBelief, (0,0,0,0,0,0))), stateActVals)
            maxActVal = max(vals)
            maxValAct = acts[ where(vals==maxActVal)[0][0] ]
            exploitOptAct = (maxValAct == 0)
            suboptActionValue = getSuboptActVal(exploitOptAct, trialStateActVals, preJumpBelief, postJump3StateBelief, belief_p_flip, trial)
            optActionValue = maxActVal
            
            if(maxValAct==0): 
                [exploitVal, exploreVal] = [maxActVal, suboptActionValue]
                p_exploit = getActionProbability(array([exploitVal, exploreVal]), exploit)
            else: 
                [exploitVal, exploreVal] = [suboptActionValue,maxActVal]
                p_exploit = getActionProbability(array([exploitVal, exploreVal]), exploit)
                

        p_explore = 1.-p_exploit
        
        # assumes the reward for the trial is in the 9th column
        trial_reward = float(subj_trials[trial][8])
        
        if (trial_reward == highestRewardSeen) or (trial_reward == highestRewardSeen + 20):
            choseExploit = 1
        else:
            choseExploit = 0
        

        if(TRIALS_START <= trial<  TRIALS_END ): log_likelihood += log( [p_explore,p_exploit][choseExploit])
        

                
        

        jumpsObserved = 0
        if(trial_reward > highestRewardSeen):
            jumpsObserved = (trial_reward - highestRewardSeen) / 10
            highestRewardSeen = trial_reward
            
            # assumes the response is in the 8th column of the datafile
            highestRawActionSeen = int(subj_trials[trial][7]) # CHANGED THIS

        num_jumps_seen += jumpsObserved


        preJumpBelief = getStateDistFromLastBelief(preJumpBelief, choseExploit, jumpsObserved, belief_p_flip)[0]

        # these are used for action selection next trial
        postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, post_vol))
        postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2]


    if(full_output):  return [-log_likelihood, model_trials]
    else:
        #print log_likelihood
        return -log_likelihood


NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]


ALL_STATE_ACT_VALS = loadAllStateActVals(NUM_TRIALS, load_cached=True)


# change this to the file with the data to model
#data = openfile("/path_to_file/datafile.dat")
data = openfile("test_datafile.dat")

# specify the path and name you want for the file that outputs the results
#f = open("/path_to_file/outputfile.dat", "w+")
f = open("outputfile.dat", "w+")

# does a grid search to find the best fitting parameters
for subj in data:
    best_subj_ll = inf
    for exploit in linspace(.0001, 0.8, 11):
        for belief_p_flip in ALL_STATE_ACT_VALS.keys(): # commented this out to do fixed p_flip
            #print exploit, belief_p_flip
            

            ll = getSoftmaxActorLikelihood([belief_p_flip], subj, exploit) 

            if (ll < best_subj_ll): [best_p_flip, best_exploit, best_subj_ll] = [belief_p_flip, exploit, ll]
    # print the results
    print subj[0][0], best_subj_ll, getBIC(best_subj_ll, 2), best_p_flip, best_exploit
    
    # write the results to the output file
    f.write( str(subj[0][0])+' '+str( best_subj_ll)+' '+str( getBIC(best_subj_ll, 2))+' '+str( best_p_flip)+' '+str( best_exploit)+' ')
    f.write('\n')
    f.flush()


