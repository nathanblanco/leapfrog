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



def doModelSimTrials(subj, cesd, exploit, belief_p_flip, sim_trials):

    belief_p_flip = round(belief_p_flip, 4)
    if((not (0 < belief_p_flip < .41)) or (not (0 < exploit < 10))): return -10000
    alpha_p_flips = array(sorted(ALL_STATE_ACT_VALS.keys()))
    try: alpha_p_flip = alpha_p_flips[alpha_p_flips <= belief_p_flip][-1]
    except: return -10000

    return getModelSimTrials(subj, cesd, exploit, alpha_p_flip, ALL_STATE_ACT_VALS[alpha_p_flip], sim_trials)


def getModelSimTrials(subj, cesd, exploit, belief_p_flip, trialStateActVals, sim_trials, beliefs_only=False, learn_p_flip=False, full_output=False, debug=False):
    highestRawActionSeen = 0 #B, right?    
    highestRewardSeen = 20 #right?

    num_jumps_seen = 0
    [a0, b0] = [belief_p_flip*10, (1-belief_p_flip)*10] #weak prior
    post_vol = (num_jumps_seen+a0) / (num_jumps_seen+a0-num_jumps_seen+b0)

    preJumpBelief = 1 # this is the belief after the last action and observation, but before a potential hidden jump; it should be used to get the following step's preJumpBelief (postJumpBelief should not be used)
    postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, belief_p_flip))
    postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2] # 
    
    model_trials = []


    for trial in range(NUM_TRIALS):
        if(beliefs_only):#SOFTMAX ON BELIEFS
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
            
            # need to output whether it was explore or exploit
            # and whether it was the better option
            # also whether it was explore or exploit- optimal
            
            if(maxValAct==0): 
                [exploitVal, exploreVal] = [maxActVal, suboptActionValue]
                p_exploit = getActionProbability(array([exploitVal, exploreVal]), exploit)
                explore_opt = 0
            else: 
                [exploitVal, exploreVal] = [suboptActionValue,maxActVal]
                p_exploit = getActionProbability(array([exploitVal, exploreVal]), exploit)
                explore_opt = 1

        [p_exploit, p_explore] = [p_exploit, 1.-p_exploit]
        
        ####
        choseExploit = getProbabilisticAction(p_exploit) # CHANGED THIS

        if choseExploit == 1:
            action = highestRawActionSeen
        else:
            action = 1 - highestRawActionSeen

        # CHANGED THIS
        trial_reward = sim_trials[0][trial][action]
        isBest = (trial_reward == max(sim_trials[0][trial]))

        jumpsObserved = 0
        if(trial_reward > highestRewardSeen):
            jumpsObserved = (trial_reward - highestRewardSeen) / 10
            highestRewardSeen = trial_reward
            highestRawActionSeen = action


        num_jumps_seen += jumpsObserved


        model_trials.append([subj, cesd, trial+1, sim_trials[0][trial][0], sim_trials[0][trial][1], action, choseExploit, int(isBest), explore_opt])
        
        if debug == True:
            print 'Rewards: %s' % sim_trials[0][trial]
            print 'Action: %s' % action
            print 'Exploit? %s' % choseExploit
            print 'Best?  %s' % isBest
            print 'prob exploit, explore  %s' % p_exploit

        preJumpBelief = getStateDistFromLastBelief(preJumpBelief, choseExploit, jumpsObserved, belief_p_flip)[0]

        # these are used for action selection next trial
        postJump3StateBelief = array(get3StateDistFromPreJumpDist(preJumpBelief, post_vol))
        postJumpBelief = postJump3StateBelief[0] + postJump3StateBelief[2]

    return model_trials

def simulate_trials(num_sims, fit_data, num_trials, pflip):

	for i in range(num_sims):

		file = open("/Users/njb786/Dropbox/School/current_projects/Leapfrog/DepressionPaper/data_analysis/fits/fitted_sims/fitted_sim_trials-%s.txt" % (i+1), "w+")
		file.write("subj cesd trial b_reward a_reward action choseExploit isBest explore_opt \n")
	
		for line in range(len(fit_data)):
			sim_trials = generateLeapfrogRewards(num_trials, p_flip)
		
			#print fit_data[line]
		
			subj = fit_data[line][0]
			cesd = fit_data[line][1]
			belief_p_flip = float(fit_data[line][4])
			exploit = float(fit_data[line][5])
		
			#subj_trials = getModelSimTrials(subj, cesd, exploit, belief_p_flip, trialStateActVals, sim_trials)
			subj_trials = doModelSimTrials(subj, cesd, exploit, belief_p_flip, sim_trials)
		
			for line in subj_trials:
				for datum in line:
					file.write(str(datum)+' ')
				file.write('\n')
				file.flush()






NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]
p_flip = 0.075

ALL_STATE_ACT_VALS = loadAllStateActVals(NUM_TRIALS, load_cached=True)

fit_data = openfile("/Users/njb786/Dropbox/School/current_projects/Leapfrog/DepressionPaper/data_analysis/fits/IAfits.txt")

num_sims = 100

simulate_trials(num_sims, fit_data, NUM_TRIALS, p_flip)










