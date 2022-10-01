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