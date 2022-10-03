from qiskit import *
import pandas as pd
from qiskit import transpile
import random
import csv
import numpy as np
import time
import itertools
import random
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


Gates = ['x', 'y', 'z', 'h', 'cx', 'swap']
gateCosts = [1, 1, 1, 2, 5, 11]

def QCtoDF(qc):
    string = qc.qasm()
    circuit = string.split(';')
    circuit = circuit[3:]
    circuit.pop(len(circuit)-1)
    #print(circuit)
    with open(r"gatesTemp.csv", 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['Gate', 'Qubit'])
        for i in range(len(circuit)):            
            circuit[i] = circuit[i].replace("\n", '')
            #print(circuit[0][1])
            temp = circuit[i].split(' ')
            #temp[1] = temp[1].split(',')
            for j in range(len(temp[1])):
                 temp[1] = temp[1].replace("q[", '')
                 temp[1] = temp[1].replace("]", '')
            if temp[0] != 'measure' and temp[0] != 'barrier' and temp[0] != 'creg':
                writer.writerow(temp)
    df = pd.DataFrame(pd.read_csv(r"gatesTemp.csv"))
    return df

def unique(list1):
  
    # initialize a null list
    unique_list = []
  
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)

def depthFinder(df):
    qubits = df['Qubit'].value_counts()
    qubits = dict(qubits)
    lst = list(qubits.items())
    #get depth
    if len(lst) > 1:
        qnum = []
        for j in range(len(lst)):
            strList = str(lst[j][0]).split(',')
            qnum.append(strList[0])
        qnum = unique(qnum)
        counts = []
        for num in qnum:
            for j in range(len(lst)):
                strList = str(lst[j][0]).split(',')
                if strList[0] == num:
                    for times in range(lst[j][1]):
                        counts.append(strList[0])
        temp = []
        for num in qnum:
            temp.append(counts.count(num))
        mx = max(temp)
        return mx 
    elif len(lst) > 0:
        return(lst[0][1])
    else:
        return(0)
    
def ComplexityFinder(qc):
    df = QCtoDF(qc)
    depth = depthFinder(df)
    #Get Cost
    cost = 0
    for i in df['Gate']:
        cost += int(gateCosts[Gates.index(i)])
        
    return cost, depth

qc = QuantumCircuit(2)
qc.x(0)
qc.cx(1, 0)
qc.z(0)
qc.h(0)
qc.x(0)
qc.y(1)

#Find Cost and Depth of any given QC
cost, depth = ComplexityFinder(qc)
# print(cost, depth)
dfFull = pd.DataFrame(pd.read_csv(r"Data//NairobiDataFull3.csv"))

for i in range(len(dfFull)):
    refCost = dfFull.loc[i, "cost"]
    refDepth = dfFull.loc[i, "depth"]
    if refCost == cost and refDepth == depth:
        set = i
        break

df = pd.read_csv(r"Data//NairobiDataFull3.csv", skiprows = set, nrows=1)
df.columns = ['cost', 'depth', 'tqc3TT', 'tqc3RT', 'tqc3Counts', 'tqc3Depth', 'tqc3Qubits', 'tqc2TT', 'tqc2RT', 'tqc2Counts', 'tqc2Depth', 'tqc2Qubits', 'tqc1TT', 'tqc1RT', 'tqc1Counts', 'tqc1Depth', 'tqc1Qubits', 'tqc0TT', 'tqc0RT', 'tqc0Counts', 'tqc0Depth', 'tqc0Qubits', 'sim']

#Get average of runtime and transpile time for each optimization level
tqc3AVG = (float(df["tqc3TT"]) + float(df["tqc3RT"]))/2
tqc2AVG = (float(df["tqc2TT"]) + float(df["tqc2RT"]))/2
tqc1AVG = (float(df["tqc1TT"]) + float(df["tqc1RT"]))/2
tqc0AVG = (float(df["tqc0TT"]) + float(df["tqc0RT"]))/2
averages = [tqc0AVG, tqc1AVG, tqc2AVG, tqc3AVG]
best = averages.index(min(tqc3AVG, tqc2AVG, tqc1AVG, tqc0AVG))
print(averages)

for i in range(len(averages)):
    if i != best:
        #check if any of the other numbers are within 5% of the best and the depth transpiled circuit is smaller
        if abs( (averages[best] - averages[i]) / float(averages[best]) )*100 <= 5 and int(df["tqc" + str(i) + "Depth"]) < int(df["tqc" + str(best) + "Depth"]):
            best = i

print(best)