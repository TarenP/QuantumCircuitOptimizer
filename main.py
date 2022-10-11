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
import time


#Redundant delete later
#-------------------------------------------------------------

from qiskit import *
import pandas as pd
from qiskit import transpile
import random
import csv
import numpy as np
from qiskit.providers.aer import AerSimulator
import time
import itertools
import random
import progressbar
import pathlib
from IPython.display import clear_output
from qiskit.tools.monitor import job_monitor

from qiskit import IBMQ, Aer
from qiskit.providers.aer.noise import NoiseModel
provider = IBMQ.load_account()
# IBMQ.load_account()
# provider = IBMQ.get_provider('ibm-q')
backend = provider.get_backend('ibm_nairobi')

qubitCount = 7
runs = 3

noise_model = NoiseModel.from_backend(backend)

# Get coupling map from backend
coupling_map = backend.configuration().coupling_map

# Get basis gates from noise model
basis_gates = noise_model.basis_gates

readTime = 0

#-----------------------------------------------------------


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

def selector(qc):
    #Remove global when packaging
    global readTime
    #Find Cost and Depth of any given QC
    cost, depth = ComplexityFinder(qc)
    # print(cost, depth)
    t0 = time.time()
    dfFull = pd.DataFrame(pd.read_csv(r"Data//NairobiDataFull3.csv"))
    t1 = time.time()
    #To Understand how much faster my method is than to generate
    #all the data on the spot
    readTime = t1-t0

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

    return best


#Delete when making into package
qc = QuantumCircuit(7)
qc.x(0)
qc.cx(1, 0)
qc.z(2)
qc.cx(4, 2)
qc.cx(2, 6)
qc.h(0)
qc.swap(3, 2)
qc.y(1)
qc.cx(0, 4)
qc.x(5)
qc.y(1)
qc.h(6)
qc.swap(5, 3)
qc.y(1)
qc.h(3)
qc.x(5)
qc.y(1)
qc.swap(1, 5)
qc.swap(2, 4)
qc.x(0)
qc.cx(6, 3)
qc.h(5)
qc.x(6)
qc.cx(1, 4)
qc.y(5)


oLevel = selector(qc)
print("Chosen opt level: ", oLevel)


# TEST CODE
realTimes = []
time0 = time.time()

start_time = time.time()
tqc =  transpile(qc, backend, optimization_level = 0)
t0 = time.time() - start_time
df = QCtoDF(tqc)
result = execute(tqc, Aer.get_backend('qasm_simulator'), coupling_map=coupling_map, basis_gates=basis_gates, noise_model=noise_model).result()
t1 = result.time_taken
realTimes.append(t1+t0)

start_time = time.time()
tqc =  transpile(qc, backend, optimization_level = 1)
t0 = time.time() - start_time
df = QCtoDF(tqc)
result = execute(tqc, Aer.get_backend('qasm_simulator'), coupling_map=coupling_map, basis_gates=basis_gates, noise_model=noise_model).result()
t1 = result.time_taken
realTimes.append(t1+t0)

start_time = time.time()
tqc =  transpile(qc, backend, optimization_level = 2)
t0 = time.time() - start_time
df = QCtoDF(tqc)
result = execute(tqc, Aer.get_backend('qasm_simulator'), coupling_map=coupling_map, basis_gates=basis_gates, noise_model=noise_model).result()
t1 = result.time_taken
realTimes.append(t1+t0)

start_time = time.time()
tqc =  transpile(qc, backend, optimization_level = 3)
t0 = time.time() - start_time
df = QCtoDF(tqc)
result = execute(tqc, Aer.get_backend('qasm_simulator'), coupling_map=coupling_map, basis_gates=basis_gates, noise_model=noise_model).result()
t1 = result.time_taken
realTimes.append(t1+t0)

time1 = time.time()
generateTime = time1-time0
print("Actual Times: ", realTimes)

print("Read Method is faster by: ", (abs(readTime - generateTime)/((readTime + generateTime)/2))*100)
