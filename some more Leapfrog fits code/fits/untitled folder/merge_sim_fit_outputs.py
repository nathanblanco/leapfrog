
    
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
      
    return alldata
    
    
def add_columns():
    
   
    
        f=open("combined_fits_to_RL_sims.txt", "w+")
        #print alldata[0]
        #for datum in alldata[0]:
        #     f.write(datum+' ')

        IAdata = openfile("IA_fits_to_RL_sims_all.dat")

        RLdata = openfile("RL_fits_to_RL_sims_all.dat")

        for line in range(len(IAdata)):
            subj = IAdata[line][0]
            cesd = IAdata[line][1]
            IAllh = str(-float(IAdata[line][2]))
            IABIC =(IAdata[line][3])
            IAtemp = IAdata[line][5]
            IAflip = IAdata[line][4]
            sim_num = IAdata[line][10]
            
            for i in range(len(RLdata)):
                if RLdata[i][0] == subj and RLdata[i][5]==sim_num:
                   RLtemp = RLdata[i][4]
                   RLllh = str(-float(RLdata[i][2]))
                   RLBIC = RLdata[i][3]

                        
            f.write(subj+' '+cesd+' '+IAflip+' '+IAtemp+' '+IAllh+' '+RLtemp+' '+RLllh+' '+IABIC+' '+RLBIC+' '+sim_num)
            f.write('\n')


add_columns()






