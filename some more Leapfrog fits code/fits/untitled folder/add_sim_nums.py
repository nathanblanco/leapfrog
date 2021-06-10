
    
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
    
   
    
        f=open("combined_fits_to_IA_sims-old.txt", "w+")
        #print alldata[0]
        #for datum in alldata[0]:
        #     f.write(datum+' ')

        IAdata = openfile("combined_fits_to_IA_sims1-10.txt")

        

        for line in IAdata:
            for datum in line:
                f.write(datum+' ')
            f.write('x \n')



add_columns()






