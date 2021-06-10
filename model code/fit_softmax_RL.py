# --------------------------------------------------------------
#  RL model:
# -This code fits the 'naive RL model'. This model simply exploits
#  the option with the highest observed reward with a certain probability,
#  and explores (chooses the lower option) otherwise. It is equivalent to
#  an RL model with a learning rate of 1 where the rewards are coded as
#  1 and 0 for the higher and lower observed rewards, respectively.
# --------------------------------------------------------------

# import some modules
from pylab import *
from numpy import *
from scipy.stats import *
from string import split

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

# computes the BIC value from the log likelihood and the number of parameters
def getBIC(LL, num_params):
    return -2*LL + num_params*log(TRIALS_END-TRIALS_START)

def getProbabilisticAction(resp_prob):
    rand_num = random()
    if(rand_num <= resp_prob):  return 1
    else:   return 0


def getActionProbability(orig_action_values, exploitation): # orig_action_values

    # converts values to 0 and 1
    if(orig_action_values[0] == orig_action_values[1]): action_values = array([1, 1])    
    elif(max(orig_action_values)==orig_action_values[0]): action_values = array([1, 0])
    else: action_values = array([ 0, 1])
    
    # does softmax action selection
    # 'exploitation' is the softmax inverse temperature parameter
    numerator = exp( action_values[0] * exploitation) # action_values
    denominator = sum( exp( action_values * exploitation) ) #action_values
    if(isinf(numerator) or isinf(denominator)):
        print action_values
        raise SystemExit, 'exp() blew up'
    return numerator / denominator

# this function computes the negative log likelihood for a given subject's data
# and parameter value
def getModelLikelihood(exploit, subj_trials):

    
    neg_log_likelihood = 0.
    
    alpha = 1.
    
    Q = array([20.0, 10.0])
    
    #c("subj", "p_flip", "trial_type", "trial", "a_reward",
    # "b_reward", "res", "rew", "RT", "junk", "junk2", "exploit",
    #"best", "nback", "cesd")

    for trial in range(TRIALS_END - TRIALS_START):
    
        # assumes the reward for the trial is in the 9th column
        trial_reward = float(subj_trials[trial][8])
        
        # assumes the reward for the trial is in the 8th column and codes as 
        subj_action = int(subj_trials[trial][7])
        
        p_right = getActionProbability(array( [Q[0], Q[1]]), exploit)
        p_left = getActionProbability(array( [Q[1], Q[0]]), exploit)

        if(TRIALS_START <= trial<  TRIALS_END ): neg_log_likelihood += log( [p_right,p_left][subj_action])

        # update the observed reward values for each option
        Q[subj_action] += alpha * (trial_reward - Q[subj_action]) 
        #print Q


    return neg_log_likelihood



NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]

# open the data file
#data = openfile("/path_to_file/datafile.dat")
data = openfile("test_datafile.dat")

#  fits the model
#  does a grid search to determine the best parameter value for each participant
for subj in data[:]:
    best_subj_ll = -inf
    for exploit in linspace(.0001, 5.0, 81):
            ll = getModelLikelihood(exploit, subj) #subj
            if (ll > best_subj_ll): [best_exploit, best_subj_ll] = [exploit, ll]
    print subj[0][0], -best_subj_ll, getBIC(best_subj_ll, 1), best_exploit



