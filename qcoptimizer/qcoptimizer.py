__author__ = "Taren Patel"
__email__ = "Tarenpatel1013@gmail.com"
__status__ = "Alpha"


from qiskit import *
import numpy as np
import pandas as pd
import csv
from itertools import combinations
from collections import OrderedDict
from scipy.fftpack import diff

sim = Aer.get_backend('qasm_simulator')
typeOfGates = ['x', 'y', 'z', 'h']
passGates = ['cx']

files = [
    'gates.csv',
    'key.csv'
]

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
            print(circuit[0][1])
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
        except:
            temp = qcDF['Qubit'][i]
            if int(temp) == qubitNum:
                lst.append(qcDF['Gate'][i])
    return lst


def enhance(keyDF, qubitGates, typeOfGates):
    print(qubitGates)
    #each qubit
    circuit = []
    for i in qubitGates:
        print(i)
        qubit = []
        temp = []
        for g in i:
            if g in typeOfGates:
                temp.append(g)
            else:
                qubit.append(temp)
                temp = []
                qubit.append(g)
        qubit.append(temp)
        circuit.append(qubit)
    # print('qubit')
    # print(circuit)
    
    #create list of all viable gate combinations that don't change the permutation of the circuit
    #each set of gates for the qubit
    print(len(circuit))
    final = [[] * 1 for i in range(len(circuit))]
    # print('final')
    # print(final)
    for q in circuit:
        for p in q:
            qc = [p]
            qnum = circuit.index(q)
            # print('qnum')
            # print(qnum)
            # print('qstring')
            # print(qString)
            # print('q')
            # print(p)
            while len(qc) > 0:
                qString = ','.join(qc[0])
                gateSets = []
                replacementTimes = []
                targetTimes = []
                replacements = []
                targets = []
                pStr = listToString(qc)
                if 'cx' not in p:
                    print('qc')
                    print(qc)
                    print('final')
                    print(final)
                    #each gate in set
                    combo = [com for sub in range(len(typeOfGates)) for com in combinations(qc[0], sub + 1)]
                    print('combo')
                    print(combo)
                    for i in range(len(combo)):
                        combo[i] = list(combo[i])
                        idxString = ','.join(combo[i])
                        if idxString in qString:
                            gateSets.append(combo[i])
                    print("gatesets")
                    print(gateSets)
                    print(len(gateSets))
                    print(gateSets)
                    print(len(gateSets))
                    #find all replacements that correspond to elements in gateSets
                    found = False
                    for n in range(len(gateSets)):
                        for m in range(len(keyDF)):
                            if keyDF['Target'][m].split(',') == gateSets[n]:
                                #if they are equal set the gate combo in final list = to replacement synonym
                                replacements.append(keyDF['Replacement'][m].split(','))
                                targets.append(gateSets[n])
                                found = True
                    if found == False:
                        for n in range(len(gateSets)):
                            targets.append(gateSets[n])
                            replacements.append(gateSets[n])

                    print('targs')      
                    print(targets)
                    print('replacements')
                    print(replacements)
                    if len(replacements) >1:
                        #find the time it takes to execute each target set of gates
                        for set in targets:
                            qc1 = QuantumCircuit(1, 1) #1 quantum, 1 classical
                            for j in set:
                                for g in j:
                                    getattr(qc1 , g)(0)
                            qc1.measure(0, 0)
                            result = execute(qc1, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
                            targetTimes.append(result.time_taken)
                        # print('target')
                        # print(len(targets))
                        # print(len(targetTimes))
                        
                        #find the time it takes to execute each replacement set of gates
                        for set in replacements:
                            qc2 = QuantumCircuit(1, 1) #1 quantum, 1 classical
                            for j in set:
                                getattr(qc2 , j)(0)
                            qc2.measure(0, 0)
                            result = execute(qc2, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
                            replacementTimes.append(result.time_taken)
                        # print(len(replacements))
                        # print(len(replacementTimes))
                                
                    
                        '''
                        Compare the two times and see which replacements reduce the most amount of time and gates
                        Figure out how to find the optimal balance and split the gates up into sets based on these qualities
                        '''
                        timeDifference = []
                        for i in range(len(replacementTimes)):
                            timeDifference.append(targetTimes[i] - replacementTimes[i])
                        # print('time difference')
                        # print(timeDifference)
                        tdIdx = timeDifference.index(max(timeDifference))
                        
                        lendifference = []
                        for i in range(len(replacementTimes)):
                            lendifference.append(len(targets[i]) - len(replacements[i]))
                        ldIdx = lendifference.index(max(lendifference))
                        
                        pStr = listToString(p)
                        
                        
                        print(timeDifference)  
                        if tdIdx == ldIdx:
                            # print(tdIdx)
                            # print(replacements)
                            targetStr = listToString(targets[tdIdx])
                            pStr = listToString(p)
                            idx = pStr.index(targetStr)
                            print(p)
                            try:
                                final[qnum].insert(pStr.index(targetStr), final[qnum].append(replacements[tdIdx]))
                            except:
                                final[qnum].append(final[qnum].append(replacements[tdIdx]))
                        else:
                            temp = []
                            # print(max(lendifference))
                            for i in range(len(timeDifference)):
                                if lendifference[i] == max(lendifference):
                                    temp.append(timeDifference[i])
                                    print(temp)
                            print(replacements)
                            print(max(temp))
                            print(timeDifference)    
                            print(timeDifference.index(max(temp)))
                            print("final")
                            print(final)
                            print('qnum')
                            print(qnum)
                            print('repplasdasndas')
                            targetStr = listToString(targets[timeDifference.index(max(temp))])
                            print(targetStr)
                            idx = pStr.index(targetStr)
                            print(idx)
                            print(qc)
                            try:
                                final[qnum].insert(pStr.index(targetStr), replacements[timeDifference.index(max(temp))])
                            except:
                                final[qnum].append(replacements[timeDifference.index(max(temp))])
                            print('targetstr')
                            print(targetStr)
                            print('str')
                            print(pStr)
                            print("final")
                            print(final)
                            print('len')
                            print(len(targetStr))
                        print(qc)
                        qcTemp = qc
                        print('qctemp')
                        print(qcTemp)
                        qc = []
                        temp = []
                        temp2 = []
                        if len(qcTemp) == 1:
                            for a in range(len(qcTemp[0])):
                                print(temp)
                                if a < idx:
                                    temp.append(qcTemp[0][a])
                                elif a > idx + len(targetStr) - 1:
                                    if len(temp) == 0:
                                        temp2.append(qcTemp[0][a])
                                    else:
                                        qc.append(temp)
                                        temp = []
                                        temp2.append(qcTemp[0][a])
                            qc.append(temp)
                            qc.append(temp2)
                        else:
                            qc.append(qcTemp[1])
                        print(qc)
                        lstToPop = []
                        for i in range(len(qc)):
                            if len(qc[i]) == 0:
                                lstToPop.append(i)
                        lstToPop.sort(reverse=True)
                        for i in lstToPop:
                            qc.pop(i)
                        print('qc')
                        print(qc)
                    else:
                        targetStr = listToString(targets)
                        print('targetStr')
                        print(targetStr)
                        idx = pStr.index(targetStr)
                        print(pStr)
                        print(idx)
                        print('targhetsaesdas')
                        print(targets)
                        try:
                            final[qnum].insert(pStr.index(targetStr), replacements[0])
                        except:
                            final[qnum].append(replacements)
                        print('old qc')
                        print(qc)
                        qcTemp = qc
                        qc = []
                        temp = []
                        temp2 = []
                        if len(qcTemp) == 1:
                            for a in range(len(qcTemp[0])):
                                print(temp)
                                if a < idx:
                                    temp.append(qcTemp[0][a])
                                elif a > idx + len(targetStr) - 1:
                                    if len(temp) == 0:
                                        temp2.append(qcTemp[0][a])
                                    else:
                                        qc.append(temp)
                                        temp = []
                                        temp2.append(qcTemp[0][a])
                            qc.append(temp)
                            qc.append(temp2)
                        else:
                            qc.append(qcTemp[1])
                        print('nmew qc')
                        print(qc)
                        lstToPop = []
                        for i in range(len(qc)):
                            if len(qc[i]) == 0:
                                lstToPop.append(i)
                                print(lstToPop)
                        lstToPop.sort(reverse=True)
                        for i in lstToPop:
                            qc.pop(i)
                        print('qc')
                        print(qc)
                    print('final')
                    print(final)
                else:
                    print('here')
                    print('here')
                    print('here')
                    print('here')
                    print('here')
                    print('qc')
                    print(qc)
                    print(qnum)
                    final[qnum].append(p)
                    print(final)
                    qc = []
                print(len(qc))
                print(len(qc))
            
    

    #remove 'none' from list
    for q in range(len(final)):
        final[q] = list(filter(None, final[q]))
        
    #create circuit
    print('final studd')
    print(final)
    print('klsjfnsdnfds')
    print(len(final))
    qcirc = QuantumCircuit(len(final), len(final))
    for qubit in range(len(final)):
        for g in final[qubit]:
            if len(g) == 3 and g[2] in passGates:
                print(g)
                print(g[0])
                print(g[1])
                print(g[2])
                getattr(qcirc, g[2])(int(g[0]), int(g[1]))
            else:
                getattr(qcirc , g[0])(qubit)
    return qcirc

    
def listToString(lst):
    delStr = str(lst)
    delStr = delStr.replace(',', '')
    delStr = delStr.replace("[", '')
    delStr = delStr.replace("]", '')
    delStr = delStr.replace("'", '')
    delStr = delStr.replace(" ", '')
    return delStr
    

def checker(qc, size):
    qc.measure(size-1, size-1)
    result = execute(qc, backend=sim, shots = 1024).result()
    #plot_histogram(counts)
    return result.time_taken



def optimize(qc):
    keyDF = KeytoDF()
    #print(keyDF)
    qubitGates = []
    qcDF = QCtoDF(qc)
    for j in range(len(qc.qubits)):
        qubitGates.append(GateList(j, qcDF))
    qc1 = enhance(keyDF, qubitGates, typeOfGates)
    # print(qc)
    # c1 = checker(qc, len(qc1.qubits))
    # c2 = checker(qc1, len(qc.qubits))
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
qc.y(0)
qc.z(0)
qc.y(0)

qc1 = optimize(qc)
print(qc)

from qiskit.visualization import plot_bloch_multivector, plot_histogram, array_to_latex
sim = Aer.get_backend('qasm_simulator')
qc.measure(1, 1)
result = execute(qc, backend=sim, shots = 1024).result()
results = result.get_counts()
print(results)
print(qc1)
qc1.measure(1, 1)
result = execute(qc1, backend=sim, shots = 1024).result()
results = result.get_counts()
print(results)