import os
from numpy import *


def openfile(filename):
    myfile = open(filename)
    alldata = myfile.readlines()
    
    for i in range(len(alldata)):
        alldata[i]=alldata[i].split()
        
    datas = []
    for line in alldata:

        datas.append(line)
      
    return datas

dir= "RL_fitted_sims/"

f = open(dir+"RL-fitted-sims-all.dat", "w+")

for i in range(1, 101):
    sim_data = openfile(dir+"RL_fitted_sim_trials-%s.txt" % i)
    


    for line in sim_data[1:]:

        for datum in line:
            f.write(datum+" ")
                
        f.write(str(i))      
        f.write('\n')

    

    
    

   	 
   	 
   	 