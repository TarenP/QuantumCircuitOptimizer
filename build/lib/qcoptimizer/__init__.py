__author__ = "Taren Patel"
__email__ = "Tarenpatel1013@gmail.com"
__status__ = "Alpha"

from qiskit import *
from qiskit import transpile
import time
import pickle
import pandas as pd
import csv
import os

Gates = ['rz', 'rx', 'ry', 'sx', 'x', 'y', 'z', 'h', 'cx', 'swap']
gateCosts = [1, 1, 1, 1, 1, 1, 1, 2, 5, 11]

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'data/PerthSimRegModel.sav')
reg =pickle.load(open(filename, 'rb'))

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
        return len(counts) 
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
        if i in Gates:
            cost += int(gateCosts[Gates.index(i)])
        else:
            cost += int(gateCosts[Gates.index(i[:2])])
        
    return cost, depth

def Average(lst):
    return sum(lst) / len(lst)

def check(x):
    return x and [x[0]]*len(x) == x

def selector(qc, backend):
    runs = 1
    
    TT = []
    Cost = []
    GC = []
    RT = []
    for run in range(runs):
        start_time = time.time()
        tqc3 =  transpile(qc, backend, optimization_level = 3)
        TT3 = time.time() - start_time
        TT.append(TT3)
        Cost3, GC3 = ComplexityFinder(tqc3)
        Cost.append(Cost3)
        GC.append(GC3)
        RT3 = reg.predict([[Cost3, GC3, 3, TT3]])
        RT.append(RT3)
    TT3 = Average(TT)
    Cost3 = Average(Cost)
    GC3 = Average(GC)
    RT3 = Average(RT)



    TT = []
    Cost = []
    GC = []
    RT = []
    for run in range(runs):
        start_time = time.time()
        tqc2 =  transpile(qc, backend, optimization_level = 2)
        TT2 = time.time() - start_time
        TT.append(TT2)
        Cost2, GC2 = ComplexityFinder(tqc2)
        Cost.append(Cost2)
        GC.append(GC2)
        RT2 = reg.predict([[Cost2, GC2, 2, TT2]])
        RT.append(RT2)
    TT2 = Average(TT)
    Cost2 = Average(Cost)
    GC2 = Average(GC)
    RT2 = Average(RT)

    TT = []
    Cost = []
    GC = []
    RT = []
    for run in range(runs):
        start_time = time.time()
        tqc1 =  transpile(qc, backend, optimization_level = 1)
        TT1 = time.time() - start_time
        TT.append(TT1)
        Cost1, GC1 = ComplexityFinder(tqc1)
        Cost.append(Cost1)
        GC.append(GC1)
        RT1 = reg.predict([[Cost1, GC1, 1, TT1]])
        RT.append(RT1)
    TT1 = Average(TT)
    Cost1 = Average(Cost)
    GC1 = Average(GC)
    RT1 = Average(RT)

    TT = []
    Cost = []
    GC = []
    RT = []
    for run in range(runs):
        start_time = time.time()
        tqc0 =  transpile(qc, backend, optimization_level = 0)
        TT0 = time.time() - start_time
        TT.append(TT0)
        Cost0, GC0 = ComplexityFinder(tqc0)
        Cost.append(Cost0)
        GC.append(GC0)
        RT0 = reg.predict([[Cost0, GC0, 0, TT0]])
        RT.append(RT0)
    TT0 = Average(TT)
    Cost0 = Average(Cost)
    GC0 = Average(GC)
    RT0 = Average(RT)
    

    #Get runtime of each optimization level for this qc
    tqc3RT = RT3[0] + TT3
    tqc2RT = RT2[0] + TT2
    tqc1RT = RT1[0] + TT1
    tqc0RT = RT0[0] + TT0
    RTs = [tqc0RT, tqc1RT, tqc2RT, tqc3RT]
    GCs = [GC0, GC1, GC2, GC3]
    Costs = [Cost0, Cost1, Cost2, Cost3]
    # best = RTs.index(min(tqc0RT, tqc1RT, tqc2RT, tqc3RT))

    #Cascade choice
    #RT
    #Gatecount
    #Cost
    optLvls = [0, 1, 2, 3]
    worst = RTs.index(max(RTs))
    optLvls.pop(worst)
    RTs.pop(worst)
    GCs.pop(worst)
    Costs.pop(worst)
    #all items are identical
    if check(Costs):
        worst = RTs.index(max(RTs))
    else:
        worst = Costs.index(max(Costs))
    optLvls.pop(worst)
    RTs.pop(worst)
    GCs.pop(worst)
    Costs.pop(worst)
    if check(GCs):
        worst = RTs.index(max(RTs))
    else:
        worst = GCs.index(max(GCs))
    optLvls.pop(worst)
    best = optLvls[0]
    
    #Check if any RTs are too close to be distinguished
    RTs = [tqc0RT, tqc1RT, tqc2RT, tqc3RT]
    GCs = [GC0, GC1, GC2, GC3]
    Costs = [Cost0, Cost1, Cost2, Cost3]
    alternatives = []
    for i in range(len(RTs)):
        if i != best:
            if (RTs[i] - RTs[best]) / RTs[best] *100 <= 30 and GCs[i] < GCs[best] and Costs[i] < Costs[best]:
                best = i
            elif (RTs[i] - RTs[best]) / RTs[best] *100 <= 5 and GCs[i] <= GCs[best] and Costs[i] <= Costs[best]:
                alternatives.append(i)

    return best, alternatives