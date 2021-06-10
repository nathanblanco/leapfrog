# --------------------------------------------------------------
# Baseline model:
# -This code fits a baseline model to Leapfrog task data.
#  The model simply assumes people choose option A with some 
#  probability and option B with the remaining probability,
#  irrespective of the history of past choices and rewards.
#  Being best fit by this model is a good indicator that the
#  participant was not engaging in the task.
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

# computes the BIC value from the negative log likelihood and the number of parameters
def getBIC(nLL, num_params):
    return 2*nLL + num_params*log(NUM_TRIALS)

# this function computes the negative log likelihood for a given subject's data
# and parameter value
def getModelLikelihood(base_rate, subj_trials):

    neg_log_likelihood = 0.


    for trial in (range(len(subj_trials))):

            B_rate = base_rate
            A_rate = 1 - base_rate

            # This assumes that the response is in the 8th column and is coded as 0 or 1
            subj_action = int(subj_trials[trial][7])


            neg_log_likelihood += log( [B_rate, A_rate][subj_action]) 


    return -neg_log_likelihood



NUM_TRIALS = 300
[TRIALS_START, TRIALS_END] = [0, 300]

# open the data file
#data = openfile("/path_to_file/datafile.dat")
data = openfile("test_datafile.dat")

#  fits the model
#  does a grid search to determine the best parameter value for each participant
for subj in data[:]:
    best_subj_ll = inf
    
    # grid search
    for base_rate in linspace(.01, 1., 171):
            ll = getModelLikelihood(base_rate, subj) #subj
            if (ll < best_subj_ll): [best_base_rate, best_subj_ll] = [base_rate, ll]
    # print subjecdt number, neg log likelihood, BIC, and base rate parameter
    print subj[0][0], best_subj_ll, getBIC(best_subj_ll, 1), best_base_rate



