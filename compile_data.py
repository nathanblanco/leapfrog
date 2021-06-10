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

# the path to the folder where the data files to be compiled are stored
dir = "data/"

# name of the combined data file to be created
filename =  "alldata.txt"

f = open(filename, "w+")

#Fits = []
files = os.listdir(dir)
for file in files:
    print file
    
    if file != ".DS_Store" and file != filename and file != '.svn' and file != 'convert_data.py':
        data = openfile(dir + file)

        for line in data[1:]:

                for i in line:
                    f.write(i+" ")
                f.write('\n')

    

    
    

   	 
   	 
   	 