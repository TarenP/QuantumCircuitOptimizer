__author__ = "Taren Patel"
__email__ = "Tarenpatel1013@gmail.com"
__status__ = "Alpha"


from qiskit import *
import numpy as np
import pandas as pd
import csv
from itertools import combinations

sim = Aer.get_backend('qasm_simulator')
typeOfGates = ['x', 'y', 'z', 'h']

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
    final = []
    #each qubit
    for i in qubitGates:
        temp = []
        qubit = []
        #each gate
        for r in i:
            if r in typeOfGates:
                temp.append(r)
            else:
                qubit.append(temp)
                temp = []
                qubit.append(r)
            #if greater than 4 items in list, check which list split will lead to the best compute time and fewest gates
        qubit.append(temp)
        print(qubit)
    
    #create list of all viable gate combinations that don't change the permutation of the circuit
    #each set of gates for the qubit
    for q in qubit:
        qString = ','.join(q)
        gateSets = []
        replacementTimes = []
        targetTimes = []
        possibilities = []
        #each gate in set
        combo = [com for sub in range(4) for com in combinations(q, sub + 1)]
        #print(combo)
        for i in range(len(combo)):
            combo[i] = list(combo[i])
            idxString = ','.join(combo[i])
            if idxString in qString:
                gateSets.append(combo[i])
        #print(q)
        #print(gateSets)
        #find all replacements that correspond to elements in gateSets
        for p in range(len(gateSets)):
            for j in range(len(keyDF)):
                if keyDF['Target'][j].split(',') == gateSets[p]:
                    #if they are equal set the gate combo in final list = to replacement synonym
                    possibilities.append(keyDF['Replacement'][j].split(','))
        print(possibilities)
        
        #find the time it takes to execute each target set of gates
        for set in gateSets:
            qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
            for j in set:
                getattr(qc , j)(0)
            qc.measure(0, 0)
            result = execute(qc, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
            targetTimes.append(result.time_taken)
        print(targetTimes)
        
        #find the time it takes to execute each replacement set of gates
        for set in possibilities:
            qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
            for j in set:
                getattr(qc , j)(0)
            qc.measure(0, 0)
            result = execute(qc, backend=Aer.get_backend('qasm_simulator'), shots = 1024).result()
            replacementTimes.append(result.time_taken)
        print(replacementTimes)
                
    
        '''
        Compare the two times and see which replacements reduce the most amount of time and gates
        Figure out how to find the optimal balance and split the gates up into sets based on these qualities
        '''
    
        # final.append(qubit)
    
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
    qc = QuantumCircuit(len(final), len(final))
    for qubit in range(len(final)):
        for g in range(len(final[qubit])):
            for j in final[qubit][g]:
                if len(j) > 1:
                    getattr(qc , j[2])(int(j[0]), int(j[1]))
                else:
                    getattr(qc , j)(qubit)
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


qc = QuantumCircuit(1, 1)
qc.x(0)
qc.h(0)
qc.z(0)
qc.y(0)
qc.z(0)
qc.z(0)
qc1 = optimize(qc)