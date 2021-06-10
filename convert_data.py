
from string import split




def openfile(filename):
    myfile = open(filename)
    alldata = myfile.readlines()
    
    for i in range(len(alldata)):
        alldata[i]=alldata[i].split()
      
    return alldata
    
    
def add_columns(alldata, filename):

    
    f=open(filename, "w+")
    
    for line in range(len(alldata)):
        #print alldata[line]
        
        if len(alldata[line]) > 6:
            if (alldata[line][7] == 'r') or (alldata[line][7] == 'l'):
                        
                for datum in alldata[line]:
                    if datum == 'r':
                        datum = '0'
                    elif datum == 'l':
                        datum = '1'
                    f.write(datum+' ')
                f.write('\n')
                f.flush()

# name of the file to be converted
filename = 'alldata.txt'
    
data = openfile(filename)

# name of the new file to be created
new_filename = 'alldata-converted.txt'

add_columns(data, new_filename)






