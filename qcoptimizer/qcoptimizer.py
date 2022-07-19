__author__ = "Taren Patel"
__email__ = "Tarenpatel1013@gmail.com"
__status__ = "Alpha"


from dataclasses import replace
from unittest.main import MAIN_EXAMPLES
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
from qiskit import *
import numpy as np
import pandas as pd
import csv
from itertools import combinations
from collections import OrderedDict
from scipy.fftpack import diff
from sympy import re, timed

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
    url='https://drive.google.com/file/d/14xmXvA6Y84nk1phQ6mht3EkOhmW_7J4L/view?usp=sharing'
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
                
    combo = [com for sub in range(4) for com in combinations(qlist, sub + 1)]
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

def sortListIdx(lst):
    li=[]
    for i in range(len(lst)):
        li.append([lst[i],i])
    li.sort()
    sort_index = []
    
    for x in li:
        sort_index.append(x[1])
    return sort_index

def bestCombo(replacements, targets, replacementTimes, targetTimes):
    #get time difference
    # print(replacements)
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


    # print(sortedTDifference)
    rOrder = []
    tOrder = []
    for i in sortedTDifference:
        # print(i)
        # print('append')
        # print(replacements[timeDifference.index(i)])
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
    # print(xList)
    yList = list_duplicates_of(qString, 'y')
    hList = list_duplicates_of(qString, 'h')
    zList = list_duplicates_of(qString, 'z')
    for i in range(len(rOrder)):
        # print('i')
        # print(i)
        # print(len(rOrder))
        # print('tOrder')
        # print(tOrder)
        # print('rOrder')
        # print(rOrder)
        # print(qString)
        # print('hlist')
        # print(hList)
        if i != 0:
            # print(qString)
            
            skip = False
            tString1 = ','.join(tOrder[i])
            tString1 = tString1.replace(',', '')
            # print(tString1)
            # print(qStringRepl)
            if tString1 in qStringRepl and len(qStringRepl) > 0:
                if len(tString1) > 1:
                    idx1 = qString.index(tString1)
                    for m in range(idx1, idx1 + len(tString1)):
                        if qString[m] == 'x':
                            xList.pop(0)
                        elif qString[m] == 'y':
                            yList.pop(0)
                        elif qString[m] == 'z':
                            print(m)
                            zList.pop(0)
                        elif qString[m] == 'h':
                            hList.pop(0)
                    
                else:
                    if tString1[0] == 'x':
                        idx1 = xList[0]
                        xList.pop(0)
                    elif tString1[0] == 'y':
                        idx1 = yList[0]
                        yList.pop(0)
                    elif tString1[0] == 'z':
                        idx1 = zList[0]
                        zList.pop(0)
                    elif tString1[0] == 'h':
                        idx1 = hList[0]
                        hList.pop(0)
                    
            else:
                skip = True
            # print(idx2)
            # length = list(range(idx2, idx2 + len(tString2)))
            # skip = False
            # for l in length:
            #     for p in alrAdded:
            #         if l in p:
            #             skip = True
            #             break
            # print(skip)
            if skip == False:
                qStringRepl = qStringRepl.replace(tString1, '')
                length = list(range(idx1, idx1 + len(tString1)))
                # print(tString1)
                # print(idx1)
                for j in range(len(lowest)):
                    if j != 0:
                        if idx1 + len(tString1) - 1 < lowest[j] and  idx1 > lowest[j - 1]:
                            qubit = insertList(qubit, j, rOrder[i])
                            targets = insertList(targets, j, tOrder[i])
                            alrAdded.insert(j, length)
                            highest.insert(j, length[-1])
                            lowest.insert(j, length[0])
                        elif idx1 > highest[j] and  idx1 + len(tString1) - 1 < lowest[j + 1]:
                            qubit = insertList(qubit, j + 1, rOrder[i])
                            targets = insertList(targets, j + 1, tOrder[i])
                            alrAdded.insert(j + 1, length)
                            highest.insert(j + 1, length[-1])
                            lowest.insert(j + 1, length[0])
                    else:
                        if idx1 + len(tString1) - 1 <= lowest[0]:               
                            qubit = insertList(qubit, 0, rOrder[i])
                            targets = insertList(targets, 0, tOrder[i])
                            alrAdded.insert(0, length)
                            highest.insert(0, length[-1])
                            lowest.insert(0, length[0])
                        elif idx1 > highest[-1]:
                            qubit = insertList(qubit, highest.index(highest[-1]) + 1, rOrder[i])
                            targets = insertList(targets, highest.index(highest[-1]) + 1, tOrder[i])
                            alrAdded.insert(highest.index(highest[-1]) + 1, length)
                            highest.insert(highest.index(highest[-1]) + 1, length[-1])
                            lowest.insert(highest.index(highest[-1]) + 1, length[0])
        else:
            tString1 = ','.join(tOrder[i])
            tString1 = tString1.replace(',', '')
            # print(tString1)
            # print(qString)
            if len(tString1) > 1:
                idx1 = qString.index(tString1)
                for m in range(idx1, idx1 + len(tString1)):
                    # print(m)
                    if qString[m] == 'x':
                        xList.remove(m)
                    elif qString[m] == 'y':
                        yList.remove(m)
                    elif qString[m] == 'z':
                        # print(m)
                        zList.remove(m)
                    elif qString[m] == 'h':
                        hList.remove(m)
                
            else:
                if tString1[0] == 'x':
                    idx1 = xList[0]
                    xList.pop(0)
                elif tString1[0] == 'y':
                    idx1 = yList[0]
                    yList.pop(0)
                elif tString1[0] == 'z':
                    idx1 = zList[0]
                    zList.pop(0)
                elif tString1[0] == 'h':
                    idx1 = hList[0]
                    hList.pop(0)
                    
            lst = list(range(idx1, idx1 + len(tString1)))
            alrAdded.append(lst)
            highest.append(lst[-1])
            lowest.append(lst[0])
            qubit = appendList(qubit, rOrder[i])
            targets = appendList(targets, tOrder[i])
            qStringRepl = qString.replace(tString1, '')
        # print('qStringRepl')
        # print(qStringRepl)
        # print(xList)
        # print(yList)
        # print(zList)
        # print(hList)
        # print(targets)
        # print('alradded')
        # print(alrAdded)
        # print('high/low')
        # print(highest)
        # print(lowest)
        # print('qubit')
        # print(qubit)
        # print('')
    # print(targets)
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

def appendList(qubit, lst):
    for i in lst:
        qubit.append(i)
    
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

def qcAppendNormal(qc, final):
    for g in final:
        #print(g)
        if len(g[1]) == 3 and g[1][2] == 'cx':
            getattr(qc, g[1][2])(int(g[1][0]), int(g[1][1]))
        elif len(g[1]) > 1:
            for l in g[1]:
                if l != 'i':
                    getattr(qc, l)(int(g[0]))
        elif g[1][0] != 'i':
            getattr(qc, g[1][0])(int(g[0]))

def organizedOrder(finalAll, targetsAll, qcDF):
    main = []
    # print(finalAll[0])
    # print(finalAll[1])
    # print(targetsAll)
    # print('')
    for q in finalAll:
        listToPop = []
        for g in range(len(q)):
            if len(q[g]) == 3 and q[g][2] =='connector':
                listToPop.append(g)
        # print(listToPop)
        listToPop.sort(reverse= True)
        # print(listToPop)
        for i in listToPop:
            # print(q[i])
            q.pop(i)
    for q in targetsAll:
        listToPop = []
        for g in range(len(q)):
            if len(q[g]) == 3 and q[g][2] =='connector':
                listToPop.append(g)
        # print(listToPop)
        listToPop.sort(reverse= True)
        # print(listToPop)
        for i in listToPop:
            # print(q[i])
            q.pop(i)
    # print(finalAll[0])
    # print(finalAll[1])
    # print(targetsAll)
    # print('')
    
    qnums = qcDF['Qubit'].tolist()
    loop = []
    while len(finalAll) > len(loop):
        if len(str(qnums[0])) == 1:
            # print('h')
            # print(qnums)
            # print(main)
            # print(finalAll)
            # print(targetsAll)
            # print('')
            temp = []
            temp.append(qnums[0])
            temp.append(finalAll[int(qnums[0])][0])
            main.append(temp)
            #store num to del
            num = qnums[0]
            # print(len(targetsAll[int(qnums[0])][0]))
            for i in range(len(targetsAll[int(qnums[0])][0])):
                qnums.remove(num)
            targetsAll[int(num)].pop(0)
            finalAll[int(num)].pop(0)
            # print(qnums)
            # print(main)
            # print(finalAll)
            # print(targetsAll)
            # print('')
        else:
            # print('h')
            # print(qnums)
            # print(main)
            # print(finalAll)
            # print(targetsAll)
            # print('')
            num = qnums[0]
            #print(len(targetsAll[int(qnums[0][0])][0]))
            temp = []
            temp.append(qnums[0][0])
            temp.append(finalAll[int(qnums[0][0])][0])
            main.append(temp)
            qnums.remove(qnums[0])
            targetsAll[int(num[0])].pop(0)
            finalAll[int(num[0])].pop(0)
            # print(qnums)
            # print(main)
            # print(finalAll)
            # print(targetsAll)
            # print('')
        #Check if lists in final are all empty
        for f in range(len(finalAll)):
            if len(finalAll[f]) == 0 and f not in loop:
                loop.append(f)
    # print(main)        
    return main
                             
def handler(keyDF, qubitGates, qcDF):
    #print(qubitGates)
    finalAll = []
    targetsAll = []
    qc = QuantumCircuit(len(qubitGates), len(qubitGates))
    for qubit in range(len(qubitGates)):
        qList = list_split(qubitGates[qubit])
        #print(qList)
        final = []
        finalTargets = []
        for gate in qList:
            # print(gate)
            if normalGate(gate):
                combos = viableCombos(gate)
                # print(combos)
                targets, replacements = comboSynonyms(keyDF, combos)
                # print('targer')
                # print(targets)
                # print('replacements')
                # print(replacements)
                replacementTimes = times(replacements)
                targetTimes = times(targets)
                #print(replacementTimes)
                # print(replacementTimes)
                # print(targets)
                rOrder, tOrder = bestCombo(replacements, targets, replacementTimes, targetTimes)
                # print('rOrder')
                # print(rOrder)
                # print('tOrder')
                # print(tOrder)
                sequence, targets = qubitOrder(rOrder, tOrder, gate)
                # print('seq')
                # print(sequence)
                # print('')
                # print(targets)
                final.append(sequence)
                finalTargets.append(gate)
            else:
                final.append(gate)
                finalTargets.append(gate)
        finalAll.append(final)
        # print(finalAll)
        targetsAll.append(finalTargets)
    #Final qc gate order, append to qc
    main = organizedOrder(finalAll, targetsAll, qcDF)
    qcAppendNormal(qc, main)
    return qc
  
def checker(qc):
    qc.measure_all()
    result = execute(qc, backend=sim, shots = 1024).result()
    results = result.get_counts()
    return results

def optimize(qc):
    keyDF = KeytoDF()
    #print(keyDF)
    qcDF = QCtoDF(qc)
    qubitGates = []
    for i in range(len(qc.qubits)):
        qubitGates.append(GateList(i, qcDF))
    qc1 = handler(keyDF, qubitGates, qcDF)
    return qc1
    # print(qc1)
    # oldqc = qc
    # newqc = qc1
    # oldcounts = checker(oldqc)
    # newcounts = checker(newqc)
    # print('old')
    # print(oldcounts)
    # print('new')
    # print(newcounts)
    # if oldcounts == newcounts:
    #     return qc1
    # else:
    #     for i in range(0, 50):
    #         qubitGates = []
    #         for i in range(len(qc.qubits)):
    #             qubitGates.append(GateList(i, qcDF))
    #         qc1 = handler(keyDF, qubitGates, qcDF)
    #         newqc = qc1
    #         newcounts = checker(newqc)
    #         if newcounts == oldcounts:
    #             return qc1
    #     print("timed out, couldn't create a quantum circuit")
        
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
