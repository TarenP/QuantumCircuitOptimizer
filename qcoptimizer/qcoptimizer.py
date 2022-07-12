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
            qubit.append(temp)
            qubit.append(i)
            temp = []  
    if temp != []:
        qubit.append(temp)  
    
<<<<<<< Updated upstream
    #create list of all viable gate combinations that don't change the permutation of the circuit
    #each set of gates for the qubit
    print(len(circuit))
    final = [[] * 1 for i in range(len(circuit))]
    # print('final')
    # print(final)
    for q in circuit:
        for p in q:
            qc = p
            qnum = circuit.index(q)
            qString = ','.join(qc)
            # print('qnum')
            # print(qnum)
            # print('qstring')
            # print(qString)
            # print('q')
            # print(p)
            while len(qc) > 0:
                gateSets = []
                replacementTimes = []
                targetTimes = []
                replacements = []
                targets = []
                if 'cx' not in p:
                    print(qc)
                    print(final)
                    #each gate in set
                    combo = [com for sub in range(len(typeOfGates)) for com in combinations(qc, sub + 1)]
                    for i in range(len(combo)):
                        combo[i] = list(combo[i])
                        #print(combo[i])
                        idxString = ','.join(combo[i][0])
                        if idxString in qString:
                            gateSets.append(combo[i])
                    print("gatesets")
                    print(gateSets)
                    print(len(gateSets))
                    for gate in gateSets:
                        # check if the count of sweet is > 1 (repeating item)
                        if gateSets.count(gate) > 1:
                            # if True, remove the first occurrence of sweet
                            gateSets.remove(gate)
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

                    # print('targs')      
                    # print(targets)
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
                        print(len(targets))
                        print(len(targetTimes))
                        
                        #find the time it takes to execute each replacement set of gates
                        for set in replacements:
                            qc2 = QuantumCircuit(1, 1) #1 quantum, 1 classical
                            for j in set:
                                getattr(qc2 , j)(0)
                            qc2.measure(0, 0)
                            result = execute(qc2, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
                            replacementTimes.append(result.time_taken)
                        print(len(replacements))
                        print(len(replacementTimes))
                                
                    
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
                        
                        #print(timeDifference)  
                        if tdIdx == ldIdx:
                            # print(tdIdx)
                            # print(replacements)
                            final[qnum].append(replacements[tdIdx])
                            delStr = str(targets[tdIdx])
                        else:
                            temp = []
                            print(max(lendifference))
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
                            print(qnum)
                            final[qnum].append(replacements[timeDifference.index(max(temp))])
                            print(final)
                            delStr = str(targets[timeDifference.index(max(temp))])
                            print(delStr)
                        print(qc)
                        delStr = delStr.replace(',', '')
                        print(delStr)
                        delStr = delStr.replace("[", '')
                        print(delStr)
                        delStr = delStr.replace("]", '')
                        print(delStr)
                        delStr = delStr.replace("'", '')
                        print(delStr)
                        delStr = delStr.replace(" ", '')
                        print(delStr)
                        qString = qString.replace(',', '')
                        print(qString)
                        qString = qString.replace(delStr, '')
                        print(qString)
                        qc = list(qString)
                        print('qc')
                        print(qc)
                    else:
                        final[qnum].append(replacements[0])
                        delStr = str(targets[0])
                        delStr = delStr.replace(',', '')
                        delStr = delStr.replace("[", '')
                        delStr = delStr.replace("]", '')
                        delStr = delStr.replace("'", '')
                        delStr = delStr.replace(" ", '')
                        #print(delStr)
                        qString = qString.replace(',', '')
                        qString = qString.replace(delStr, '')
                        qc = list(qString)
                        print('qc')
                        print(qc)
                else:
                    print('qc')
                    print(qc)
                    print(qnum)
                    final[qnum].append(p)
                    qc = []
            
        print(final)
    
    #qubit
    for n in range(len(final)):
        #gate combinations in qubit
        for i in range(len(final[n])):
                #crossreference each target in df with gate combo
                for j in range(len(keyDF)):
                    if keyDF['Target'][j].split(',') == final[n][i]:
                        #if they are equal set the gate combo in final list = to replacement synonym
                        final[n][i] = keyDF['Replacement'][j].split(',')

    #create circuit
    print(len(final))
    qc = QuantumCircuit(len(final), len(final))
    for qubit in range(len(final)):
        for g in range(len(final[qubit])):
            for j in final[qubit][g]:
                print("final[qubit][g]")
                print(j)
                if j in passGates:
                    getattr(qc , final[qubit][g][2])(int(final[qubit][g][0]), int(final[qubit][g][1]))
                elif j in typeOfGates:
                    getattr(qc , j)(qubit)
    return qc
=======
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
            getattr(qc1 , g)(0)
        qc1.measure(0, 0)
        result = execute(qc1, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
        times.append(result.time_taken)
    
    return times

def comboSynonyms(keyDF, combos):
    replacements = []
    targets = []
    for combo in combos:
        combo = list(combo)
        for m in range(len(keyDF)):
            if combo == keyDF['Target'][m].split(','):
                #if they are equal set the gate combo in final list = to replacement synonym
                replacements.append(keyDF['Replacement'][m].split(','))
                targets.append(keyDF['Target'][m].split(','))
    return targets, replacements

def bestCombo(replacements, replacementTimes, targetTimes):
    print('replacements')
    print(replacements)
    #get time difference
    timeDifference = []
    for t in range(len(targetTimes)):
        timeDifference.append(targetTimes[t] - replacementTimes[t])

    #get the lengths of each element in replacements list
    lengths = []
    for i in replacements:
        lengths.append(len(i))
        
    #acquire index of replacements with smallest gate count
    idxs = []
    for i in range(len(replacements)):
        if len(replacements[i]) == min(lengths):
            idxs.append(i)
    
    #get replacement with smallest gate count and biggest time difference between target and replacements
    if len(idxs) > 0:
        largest = 0
        for i in idxs:
            if largest == 0:
                largest = timeDifference[i]
            elif timeDifference[i] > largest:
                largest = timeDifference[i]
        print('largest')
        print(largest)        
        return replacements[timeDifference.index(largest)], timeDifference.index(largest)
    else:
        return None, None
            
def shortenedGate(target, gate):
    qString = ','.join(gate)
    qString = qString.replace(',', '')
    print(qString)
    tString = ','.join(target)
    tString = tString.replace(',', '')
    print(tString)
    idx = qString.index(tString)
    print(idx)
            
def enhance(keyDF, qubitGates, typeOfGates):
    #print(qubitGates)
    for qubit in qubitGates:
        qList = list_split(qubit)
        for gate in qList:
           if normalGate(gate):
                combos = viableCombos(gate)
                targets, replacements = comboSynonyms(keyDF, combos)
                # print('targets')
                # print(targets)
                # print('replacements')
                # print(replacements)
                replacementTimes = times(replacements)
                targetTimes = times(targets)
                # print(replacementTimes)
                # print(targets)
                best, idx = bestCombo(replacements, replacementTimes, targetTimes)
                #if replacement gate is a gate vs a replacement of no gate
                if idx != None:
                    print('targets')
                    print(targets[idx])
                    shortenedGate(targets[idx], gate)
            
            
    # qc = QuantumCircuit(len(final), len(final))
    # for qubit in range(len(final)):
    #     for g in final[qubit]:
    #         if len(g) == 3 and g[2] in passGates:
    #             print(g)
    #             print(g[0])
    #             print(g[1])
    #             print(g[2])
    #             getattr(qc, g[2])(int(g[0]), int(g[1]))
    #         else:
    #             getattr(qc , g[0])(qubit)
    # return qc
>>>>>>> Stashed changes

    


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
    qc1 = enhance(keyDF, qubitGates, typeOfGates)
    #print(qc)
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
qc.z(0)
qc.y(0)
qc.z(0)
qc.y(0)
qc.y(0)
qc.x(0)
qc.h(0)
qc.h(0)
qc.z(0)
qc.y(0)
qc.z(0)
qc.y(0)
qc.y(0)
qc.x(1)
qc.cx(1, 0)
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes

qc1 = optimize(qc)
# print(qc)

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