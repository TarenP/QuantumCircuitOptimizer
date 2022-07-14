__author__ = "Taren Patel"
__email__ = "Tarenpatel1013@gmail.com"
__status__ = "Alpha"


from dataclasses import replace
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
from qiskit import *
import numpy as np
import pandas as pd
import csv
from itertools import combinations
from collections import OrderedDict
from scipy.fftpack import diff
from sympy import timed

sim = Aer.get_backend('qasm_simulator')
typeOfGates = ['x', 'y', 'z', 'h', 'i']
passGates = ['cx', 'connector']


def QCtoDF(qc):
    string = qc.qasm()
    circuit = string.split(';')
    circuit = circuit[4:]
    circuit.pop(len(circuit)-1)
    #print(circuit)
    with open(r"gates.csv", 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['Gate', 'Qubit'])
        for i in range(len(circuit)):
            temp = ()
            circuit[i] = circuit[i].replace("\n", '')
            #print(circuit[0][1])
            temp = circuit[i].split(' ')
            #temp[1] = temp[1].split(',')
            for j in range(len(temp[1])):
                 temp[1] = temp[1].replace("q[", '')
                 temp[1] = temp[1].replace("]", '')
            writer.writerow(temp)
    df = pd.DataFrame(pd.read_csv(r"gates.csv"))
    return df


#Clean up the data in csv to fit conventional list look
def KeytoDF():
    url='https://drive.google.com/file/d/1VdJTGwXUYv-ZnJNoF3SAfqzL5FOjWSNS/view?usp=sharing'
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    df = df.fillna('i')
    for r in range(len(df)):
        try:
            df['Replacement'][r] = df['Replacement'][r].replace("('", '')
            df['Replacement'][r] = df['Replacement'][r].replace(")", '')
            df['Replacement'][r] = df['Replacement'][r].replace("'", '')
            df['Replacement'][r] = df['Replacement'][r].replace(" ", '')
            temp1 = df['Replacement'][r].split(',')
            for i in range(len(temp1)):
                if temp1[i] == '':
                    temp1.pop(i)
                    df['Replacement'][r] = df['Replacement'][r].replace(",", '')
            df['Target'][r] = df['Target'][r].replace("('", '')
            df['Target'][r] = df['Target'][r].replace(")", '')
            df['Target'][r] = df['Target'][r].replace("'", '')
            df['Target'][r] = df['Target'][r].replace(" ", '')
            temp2 = df['Target'][r].split(',')
            for i in range(len(temp2)):
                if temp2[i] == '':
                    temp2.pop(i)
                    df['Target'][r] = df['Target'][r].replace(",", '')
        except:
            pass
    return df

def normalGate(gate):
    for i in gate:
        if i in passGates:
            return False
    
    return True

#generate a list of the gates on a given qubit
def GateList(qubitNum, qcDF):
    lst = []
    for i in range(len(qcDF)):
        temp = []
        try:
            temp = qcDF['Qubit'][i].split(',')
            if int(temp[0]) == qubitNum:
                if qcDF['Gate'][i] == 'cx':
                    temp.append("cx")
                    lst.append(temp)
                else:
                    lst.append(qcDF['Gate'][i])
            elif len(temp) > 1:
                if int(temp[1]) == qubitNum:
                    temp.append("connector")
                    lst.append(temp)
        except:
            temp = qcDF['Qubit'][i]
            if int(temp) == qubitNum:
                lst.append(qcDF['Gate'][i])
    return lst

def list_split(l):
    elements = []
    for i in range(len(l)):
        if isinstance(l[i], list):
            elements.append(l[i])
    qubit = []
    temp = []
    for i in l:
        if i not in elements:
            temp.append(i)
        else:
            if temp != []:
                qubit.append(temp)
            qubit.append(i)
            temp = []  
    if temp != []:
        qubit.append(temp)  
    
    return qubit
    
def viableCombos(qlist):
                
    combo = [com for sub in range(len(typeOfGates)) for com in combinations(qlist, sub + 1)]
    combos = []
    qString = ','.join(qlist)
    for c in combo:
        idxString = ','.join(c)
        if idxString in qString:
            combos.append(c)
    return combos
            
def times(lst):
    times = []
    for combo in lst:
        qc1 = QuantumCircuit(1, 1) #1 quantum, 1 classical
        for g in combo:
            #check if id gate; add id gate
            if g != 'i':
                getattr(qc1 , 'id')(0)
            else:
                getattr(qc1 , g)(0)
        qc1.measure(0, 0)
        result = execute(qc1, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
        times.append(result.time_taken)
    
    return times

def comboSynonyms(keyDF, combos):
    replacements = []
    targets = []
    for combo in combos:
        found = False
        combo = list(combo)
        for m in range(len(keyDF)):
            if combo == keyDF['Target'][m].split(','):
                #if they are equal set the gate combo in final list = to replacement synonym

                
                replacements.append(keyDF['Replacement'][m].split(','))
                targets.append(keyDF['Target'][m].split(','))
                # print('replacements')
                # print(replacements)
                # print('targets')
                # print(targets)
                found = True
        if found == False:
            replacements.append(combo)
            targets.append(combo)
    
    return targets, replacements

def sortListIdxsRev(lst):
    #https://www.geeksforgeeks.org/python-returning-index-of-a-sorted-list/
    li=[]
    for i in range(len(lst)):
        li.append([lst[i],i])
    li.sort(reverse = True)
    sort_index = []
    
    for x in li:
        sort_index.append(x[1])
    return sort_index

def bestCombo(replacements, targets, replacementTimes, targetTimes):
    #get time difference
    #print(replacements)
    timeDifference = []
    for t in range(len(targetTimes)):
        timeDifference.append(targetTimes[t] - replacementTimes[t])

    #get the lengths of each element in replacements and targets list
    
    rlengths = []
    for i in replacements:
        if i[0] == 'i':
            rlengths.append(0)
        else:
            rlengths.append(len(i)) 
        
    tlengths = []
    for i in targets:
        tlengths.append(len(i))    
        
    lenDifference = []
    for l in range(len(rlengths)):
        lenDifference.append(tlengths[l] - rlengths[l])
        
    #Sort a list in python and then return the index of elements in sorted order
    lenSortIdx = sortListIdxsRev(lenDifference)
    #print(lenSortIdx)
    lenDifference.sort(reverse = True)
    
    sortedTDifference = []
    for i in lenSortIdx:
        sortedTDifference.append(timeDifference[i])

    rOrder = []
    tOrder = []
    for i in sortedTDifference:
        rOrder.append(replacements[timeDifference.index(i)])
        tOrder.append(targets[timeDifference.index(i)])
    
    
    # print(rOrder)
    # print(tOrder)
    return rOrder, tOrder
            
def qubitOrder(rOrder, tOrder, gate):
    qString = ','.join(gate)
    qString = qString.replace(',', '')
    # print(qString)
    
    # print(tOrder)
    # print(rOrder)
    

    qubit = []
    targets = []
    alrAdded = []
    highest = []
    lowest = []
    xList = list_duplicates_of(qString, 'x')
    yList = list_duplicates_of(qString, 'y')
    hList = list_duplicates_of(qString, 'h')
    zList = list_duplicates_of(qString, 'z')
    
    refxList = list_duplicates_of(qString, 'x')
    refyList = list_duplicates_of(qString, 'y')
    refhList = list_duplicates_of(qString, 'h')
    refzList = list_duplicates_of(qString, 'z')
    for i in range(len(rOrder)):
        # print('tOrder')
        # print(tOrder)
        # print('rOrder')
        # print(rOrder)
        # print(qString)
        # print('hlist')
        # print(hList)
        if i != 0:
            idx1 = []
            tString1 = ','.join(tOrder[i-1])
            tString1 = tString1.replace(',', '')
            for a in range(len(tString1)):
                if a == 0:
                    if tString1[a] == 'x' and len(refxList) > 0:
                        idx1 = refxList[0]
                        refxList.pop(0)
                    elif tString1[a] == 'y' and len(refyList) > 0:
                        idx1 = refyList[0]
                        refyList.pop(0)
                    elif tString1[a] == 'z' and len(refzList) > 0:
                        idx1 = refzList[0]
                        refzList.pop(0)
                    elif tString1[a] == 'h' and len(refhList) > 0:
                        idx1 = refhList[0]
                        refhList.pop(0)
                else:
                    if tString1[a] == 'x' and len(refxList) > 0:
                        refxList.pop(0)
                    elif tString1[a] == 'y' and len(refyList) > 0:
                        refyList.pop(0)
                    elif tString1[a] == 'z' and len(refzList) > 0:
                        refzList.pop(0)
                    elif tString1[a] == 'h' and len(refhList) > 0:
                        refhList.pop(0)
            if idx1 == []: 
                idx1 = qString.index(tString1)
            tString2 = ','.join(tOrder[i])
            tString2 = tString2.replace(',', '')
            idx2 = []
            for a in range(len(tString2)):
                if a == 0:
                    if tString2[a] == 'x' and len(xList) > 0:
                        idx2 = xList[0]
                        xList.pop(0)
                    elif tString2[a] == 'y' and len(yList) > 0:
                        idx2 = yList[0]
                        yList.pop(0)
                    elif tString2[a] == 'z' and len(zList) > 0:
                        idx2 = zList[0]
                        zList.pop(0)
                    elif tString2[a] == 'h' and len(hList) > 0:
                        idx2 = hList[0]
                        hList.pop(0)
                else:
                    if tString2[a] == 'x' and len(xList) > 0:
                        xList.pop(0)
                    elif tString2[a] == 'y' and len(yList) > 0:
                        yList.pop(0)
                    elif tString2[a] == 'z' and len(zList) > 0:
                        zList.pop(0)
                    elif tString2[a] == 'h' and len(hList) > 0:
                        hList.pop(0)
            if idx2 == []: 
                idx2 = qString.index(tString2)
            length = list(range(idx2, idx2 + len(tString2)))
            skip = False
            for l in length:
                for p in alrAdded:
                    if l in p:
                        skip = True
                        break
            if skip == False:
                # print(tString1)
                # print(idx1)
                # print(tString2)
                # print(idx2)
                if idx2 + len(tString2) - 1 < idx1:
                    for j in range(len(lowest)):
                        if j != 0:
                            if idx2 + len(tString2) - 1 < lowest[j] and  idx2 > lowest[j - 1]:
                                qubit = insertList(qubit, j, rOrder[i])
                                targets = insertList(targets, j, tOrder[i])
                                alrAdded.insert(j, length)
                                highest.insert(j, length[-1])
                                lowest.insert(j, length[0])
                            elif idx2 > highest[j] and  idx2 + len(tString2) - 1 < lowest[j + 1]:
                                qubit = insertList(qubit, j + 1, rOrder[i])
                                alrAdded.insert(j + 1, length)
                                highest.insert(j + 1, length[-1])
                                lowest.insert(j + 1, length[0])
                        else:
                            if idx2 + len(tString2) - 1 <= lowest[0]:               
                                qubit = insertList(qubit, 0, rOrder[i])
                                targets = insertList(targets, 0, tOrder[i])
                                alrAdded.insert(0, length)
                                highest.insert(0, length[-1])
                                lowest.insert(0, length[0])
                            elif idx2 > highest[-1]:
                                qubit = insertList(qubit, highest.index(highest[-1]) + 1, rOrder[i])
                                targets = insertList(targets, highest.index(highest[-1]) + 1, tOrder[i])
                                alrAdded.insert(highest.index(highest[-1]) + 1, length)
                                highest.insert(highest.index(highest[-1]) + 1, length[-1])
                                lowest.insert(highest.index(highest[-1]) + 1, length[0])
                elif idx2 > idx1 + len(tString1) - 1:
                    for j in range(len(lowest)):
                        if j != 0:
                            if idx2 + len(tString2) - 1 < lowest[j] and  idx2 > lowest[j - 1]:
                                qubit = insertList(qubit, j, rOrder[i])
                                targets = insertList(targets, j, tOrder[i])
                                alrAdded.insert(j, length)
                                highest.insert(j, length[-1])
                                lowest.insert(j, length[0])
                            elif idx2 > highest[j] and  idx2 + len(tString2) - 1 < lowest[j + 1]:
                                qubit = insertList(qubit, j + 1, rOrder[i])
                                targets = insertList(targets, j + 1, tOrder[i])
                                alrAdded.insert(j + 1, length)
                                highest.insert(j + 1, length[-1])
                                lowest.insert(j + 1, length[0])
                        else:
                            if idx2 + len(tString2) - 1 <= lowest[0]:               
                                qubit = insertList(qubit, 0, rOrder[i])
                                targets = insertList(targets, 0, tOrder[i])
                                alrAdded.insert(0, length)
                                highest.insert(0, length[-1])
                                lowest.insert(0, length[0])
                            elif idx2 > highest[-1]:
                                qubit = insertList(qubit, highest.index(highest[-1]) + 1, rOrder[i])
                                targets = insertList(targets, highest.index(highest[-1]) + 1, tOrder[i])
                                alrAdded.insert(highest.index(highest[-1]) + 1, length)
                                highest.insert(highest.index(highest[-1]) + 1, length[-1])
                                lowest.insert(highest.index(highest[-1]) + 1, length[0]) 
        else:
            idx1 = []
            tString1 = ','.join(tOrder[i])
            tString1 = tString1.replace(',', '')
            # print(tString1)
            for a in range(len(tString1)):
                if a == 0:
                    if tString1[a] == 'x' and len(xList) > 0:
                        idx1 = xList[0]
                        xList.pop(0)
                    elif tString1[a] == 'y' and len(yList) > 0:
                        idx1 = yList[0]
                        yList.pop(0)
                    elif tString1[a] == 'z' and len(zList) > 0:
                        idx1 = zList[0]
                        zList.pop(0)
                    elif tString1[a] == 'h' and len(hList) > 0:
                        idx1 = hList[0]
                        hList.pop(0)
                else:
                    if tString1[a] == 'x' and len(xList) > 0:
                        xList.pop(0)
                    elif tString1[a] == 'y' and len(yList) > 0:
                        yList.pop(0)
                    elif tString1[a] == 'z' and len(zList) > 0:
                        zList.pop(0)
                    elif tString1[a] == 'h' and len(hList) > 0:
                        hList.pop(0)
            if idx1 == []: 
                idx1 = qString.index(tString1)
            lst = list(range(idx1, idx1 + len(tString1)))
            alrAdded.append(lst)
            highest.append(lst[-1])
            lowest.append(lst[0])
            qubit = insertList(qubit, 0, rOrder[i])
            targets = insertList(targets, 0, tOrder[i])
            
        # print('alradded')
        # print(alrAdded)
        # print('high/low')
        # print(highest)
        # print(lowest)
        # print('qubit')
        # print(qubit)
    return qubit, targets

def insertList(qubit, pos, lst):
    for i in range(len(lst)):
        qubit.insert(i + pos, lst[i])
    
    return qubit
            
def list_duplicates_of(seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs

def qcAppendNormal(qc, sequence, qubit):
    for g in sequence:
        if g != 'i':
            getattr(qc, g)(qubit)

def qcAppendIrregular(qc, sequence):
    if sequence[2] != "connector":
        getattr(qc, sequence[2])(int(sequence[0]), int(sequence[1]))

def organizedOrder(finalAll, targetsAll, qcDF):
    main = []
    #print(organizer)
    gateList = qcDF['Gate'].tolist()
    
    qubitList = qcDF['Qubit'].tolist()
    
    print(gateList)
    print(qubitList)
    print(finalAll)
    print(targetsAll)
    
    #remove connected markers
    listToPop = []
    for q in finalAll:
        for combo in range(len(q)):
            if len(q[combo]) == 3 and q[combo][2] == 'connector':
                listToPop.append(combo)
        listToPop.sort(reverse=True)
        for i in listToPop:
            q.pop(i)
    
    #every item
    num = -1
    q = 0
    while len(qubitList) > 0:
        print(len(qubitList))
        #if q not in qExclude:
        temp = []
        try: 
            qubitList[q] = int(qubitList[q])
        except:
            pass
        #print(qubitList[q])
        #print(finalAll)
        if isinstance(qubitList[q], int) and qubitList[q] != num:
            temp.append(qubitList[q])
            temp.append(finalAll[qubitList[q]][0])
            main.append(temp)
            num = qubitList[q]
            #print(len(targetsAll[qubitList[q]][0]))
            for j in range(len(targetsAll[qubitList[q]][0]) - 1):
                for i in range(len(qubitList)):
                    if qubitList[i] == str(num):
                        qubitList.pop(i)
                        break
            #print(qubitList)
            finalAll[int(qubitList[q])].pop(0)
            qubitList.pop(0)
        elif isinstance(qubitList[q], str):
            main.append(finalAll[int(qubitList[q][0])][0])
            finalAll[int(qubitList[q][0])].pop(0)
            qubitList.pop(0)
            num = -1
        print(main)
    
    #everything until number change is index 0 of finalAll
    
    
    
    #         #if cx
    #         if len(combo) >= 4 and combo[2] == 'c':
    #             for g in range(len(targetsAll[int(combo[1])])):
    #                 gcombo = ''.join(targetsAll[int(combo[1])][g])
    #                 #if connector
    #                 if len(gcombo) >= 10 and gcombo[3] == 'o':
    #                     if gcombo[0] == combo[1] and gcombo[1] == combo[0]:
    #                         if g != 0:
    #                             main.append(targetsAll[int(combo[1])][g - 1])
    #                             main.append(targetsAll[int(combo[1])][g])
    #                             targetsAll[int(combo[1])].pop(g-1)
    #                             targetsAll[int(combo[1])].pop(g)
    #                             break
                        
    #         gateStr = gateStr.replace(combo, '')
    #         #print(gateStr)
    #         main.append(finalAll[qubit][set])
    #     print(main)
                
        
        
def enhance(keyDF, qubitGates, qcDF):
    #print(qubitGates)
    finalAll = []
    targetsAll = []
    qc = QuantumCircuit(len(qubitGates), len(qubitGates))
    for qubit in range(len(qubitGates)):
        qList = list_split(qubitGates[qubit])
        final = []
        finalTargets = []
        for gate in qList:
            if normalGate(gate):
                combos = viableCombos(gate)
                targets, replacements = comboSynonyms(keyDF, combos)
                replacementTimes = times(replacements)
                targetTimes = times(targets)
                #print(replacementTimes)
                # print(replacementTimes)
                # print(targets)
                rOrder, tOrder = bestCombo(replacements, targets, replacementTimes, targetTimes)
                sequence, targets = qubitOrder(rOrder, tOrder, gate)
                final.append(sequence)
                finalTargets.append(targets)
                #qcAppendNormal(qc, sequence, qubit)
            else:
                final.append(gate)
                finalTargets.append(gate)
                #qcAppendIrregular(qc, gate)
        finalAll.append(final)
        targetsAll.append(finalTargets)
    #print(len(organizer))
    organizedOrder(finalAll, targetsAll, qcDF)
    return qc

    


def checker(qc, size):
    qc.measure(size-1, size-1)
    result = execute(qc, backend=sim, shots = 1024).result()
    #plot_histogram(counts)
    return result.time_taken



def optimize(qc):
    keyDF = KeytoDF()
    #print(keyDF)
    qcDF = QCtoDF(qc)
    qubitGates = []
    for i in range(len(qc.qubits)):
        qubitGates.append(GateList(i, qcDF))
    qc1 = enhance(keyDF, qubitGates, qcDF)
    # c1 = checker(qc1, len(qc1.qubits))
    # c2 = checker(qc, len(qc.qubits))
    # print(c1)
    # print(c2)
    # if c1 < c2:
    #     print("Optimized QC is faster by: ")
    #     print(c2-c1)
        
    # else:
    #     print("Optimized QC is slower by: ")
    #     print(c1-c2)
    
    return qc1


qc = QuantumCircuit(2, 2)
qc.x(0)
qc.h(0)
qc.h(0)
qc.z(0)
qc.y(0)
qc.x(1)
qc.x(0)
qc.y(0)
qc.cx(0, 1)
qc.x(1)
qc.x(1)
qc.cx(1, 0)
#print(qc)
qc1 = optimize(qc)
# #print(qc1)
# from qiskit.visualization import plot_bloch_multivector, plot_histogram, array_to_latex
# sim = Aer.get_backend('qasm_simulator')
# qc.measure(1, 1)
# result = execute(qc, backend=sim, shots = 1024).result()
# results = result.get_counts()
# print(results)
# print(qc1)
# qc1.measure(1, 1)
# result = execute(qc1, backend=sim, shots = 1024).result()
# results = result.get_counts()
# print(results)