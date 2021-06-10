from numpy import *
from os import system

'''
possibly do this with subprocess.Popen()
e.g.,
proc = subprocess.Popen(["r.mapcalc", "blabla=2*bla"], 
stdout=file(os.devnull, "w"))
retcode = proc.wait()
'''

pomdpStrTemplate = """ # Otto, Knox, and Love's Dynamic 2-armed bandit (after conversion to a two-state POMDP problem)
# POMDP spec for jump probability of %(jumpProb)s

# It should be fine for the actual action indicated by "exploit" and "explore" to change, since 
# the label of the maximizing action in future time steps doesn't have a bearing on the value
# in those future time steps. (I'm not totally sure about this though.)

discount: 1.0
values: reward
states: 9 # 0, 1, or 2 unobserved jumps; afterstates used for observations: (state 0, exploit(0)), (1, 0), (2,0), (0, explore(1)), (1,1), (2,1)
actions: exploit explore obsAct
observations: 3 # no jump, 1 jump, and 2 jumps

# transition involves possible observation of jumps and then a possible new jump
T: exploit
0 0 0 1 0 0 0 0 0 
0 0 0 0 1 0 0 0 0 
0 0 0 0 0 1 0 0 0 
0 0 0 1 0 0 0 0 0 
0 0 0 0 1 0 0 0 0 
0 0 0 0 0 1 0 0 0 
0 0 0 0 0 0 1 0 0 
0 0 0 0 0 0 0 1 0 
0 0 0 0 0 0 0 0 1 

T: explore
0 0 0 0 0 0 1 0 0 
0 0 0 0 0 0 0 1 0 
0 0 0 0 0 0 0 0 1 
0 0 0 1 0 0 0 0 0 
0 0 0 0 1 0 0 0 0 
0 0 0 0 0 1 0 0 0 
0 0 0 0 0 0 1 0 0 
0 0 0 0 0 0 0 1 0 
0 0 0 0 0 0 0 0 1 

T: obsAct
1 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0
0 0 1 0 0 0 0 0 0
%(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0 0
0 %(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0   # before possible new jump, exploit will not observe the one jump already unobserved
%(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0 0   # before possible new jump, exploit will observe the two unobserved jumps
%(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0 0
%(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0 0   # before possible new jump, explore will observe the one jump already unobserved
0 %(noJumpProb)s %(jumpProb)s 0 0 0 0 0 0   # before possible new jump, explore will observe the one of the two unobserved jumps


# each row is a different state, each column is a different observation, and the entries are probabilities of seeing an observation given the state and action
O: * 
0.333333 0.333333 0.333333
0.333333 0.333333 0.333333
0.333333 0.333333 0.333333
1 0 0
1 0 0  # unobserved jump will not be seen by exploit
0 0 1  # exploit will see both unobserved jumps
1 0 0
0 1 0
0 1 0



# The accumulated reward in this reformulated version (where reward doesn't keep climbing) 
# corresponds to how much more than the minimum possible reward is received in the real 
# (climbing reward) version.
R: exploit : 0 : * : * 10
R: exploit : 1 : * : * 0
R: exploit : 2 : * : * 10
R: exploit : 3 : * : * -1000
R: exploit : 4 : * : * -1000
R: exploit : 5 : * : * -1000
R: exploit : 6 : * : * -1000
R: exploit : 7 : * : * -1000
R: exploit : 8 : * : * -1000

R: explore: 0 : * : * 0
R: explore: 1 : * : * 10
R: explore: 2 : * : * 0
R: explore : 3 : * : * -1000
R: explore : 4 : * : * -1000
R: explore : 5 : * : * -1000
R: explore : 6 : * : * -1000
R: explore : 7 : * : * -1000
R: explore : 8 : * : * -1000

R: obsAct : 0 : * : * -1000
R: obsAct : 1 : * : * -1000
R: obsAct : 2 : * : * -1000
R: obsAct : 3 : * : * 0
R: obsAct : 4 : * : * 0
R: obsAct : 5 : * : * 0
R: obsAct : 6 : * : * 0
R: obsAct : 7 : * : * 0
R: obsAct : 8 : * : * 0 """


def generateAlphas(p_flip, num_trials):
    subs = {'jumpProb': p_flip, 'noJumpProb': 1 - p_flip}
    pomdpStr = pomdpStrTemplate % subs
    temp = open('pomdp_specs/leapfrog'+str(p_flip)+'.pomdp', 'w')
    temp.write(pomdpStr)
    temp.close()

    alpha_dir = 'alphas/alphas_'+str(num_trials)+'_trial_'+str(p_flip)
    system('mkdir '+alpha_dir)
    system('./pomdp-solve-5.3/src/pomdp-solve -pomdp ' + 'pomdp_specs/leapfrog'+str(p_flip)+'.pomdp ' + \
               '-horizon '+str(num_trials)+' -save_all true > log.dat')
    system('rm pomdp_specs/*.pg*')
    system('mv pomdp_specs/*.alpha* ./'+alpha_dir + '/.')


NUM_TRIALS = 300

for p_flip in linspace(.01, .21, 41): #: #linspace(.01, .21, 41): #[.075]
    print 'generating alphas:', p_flip
    generateAlphas(p_flip, (NUM_TRIALS*2)-1)

