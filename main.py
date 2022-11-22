from qiskit import *
import pandas as pd
from qiskit import transpile
import csv
import time
import numpy as np
import pandas as pd
import time
IBMQ.load_account()
provider = IBMQ.get_provider('ibm-q')
backend = provider.get_backend('ibmq_manila')
from qiskit import IBMQ, Aer
from qiskit.providers.aer.noise import NoiseModel

qubitCount = 7
runs = 3

noise_model = NoiseModel.from_backend(backend)

# Get coupling map from backend
coupling_map = backend.configuration().coupling_map

# Get basis gates from noise model
basis_gates = noise_model.basis_gates

readTime = 0

dataFile = "Data//NairobiDataAVG1.csv"
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
    print(cost, depth)

    t0 = time.time()
    dfFull = pd.read_csv(dataFile)
    t1 = time.time()
    #To Understand how much faster my method is than to generate
    #all the data on the spot
    readTime = t1-t0

    for i in range(len(dfFull)):
        refCost = dfFull.loc[i, "cost"]
        refDepth = dfFull.loc[i, "depth"]
        if refCost == cost and refDepth == depth:
            rowSet = i
            break

    df = pd.read_csv(dataFile, skiprows = rowSet, nrows=1)
    # df.columns = ['cost', 'depth', 'tqc3TT', 'tqc3RT', 'tqc3Counts', 'tqc3Depth', 'tqc3Qubits', 'tqc2TT', 'tqc2RT', 'tqc2Counts', 'tqc2Depth', 'tqc2Qubits', 'tqc1TT', 'tqc1RT', 'tqc1Counts', 'tqc1Depth', 'tqc1Qubits', 'tqc0TT', 'tqc0RT', 'tqc0Counts', 'tqc0Depth', 'tqc0Qubits', 'sim']
    #For AVG df
    df.columns = ['cost', 'depth', 'tqc3TT', 'tqc3RT', 'tqc3Depth', 'tqc2TT', 'tqc2RT', 'tqc2Depth', 'tqc1TT', 'tqc1RT', 'tqc1Depth', 'tqc0TT', 'tqc0RT', 'tqc0Depth']
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
            print(i)
            print((abs(averages[best] - averages[i]) / ((float(averages[best]) + float(averages[i]))/2 )*100))
            print(int(df["tqc" + str(i) + "Depth"]), int(df["tqc" + str(best) + "Depth"]))
            #check if any of the other numbers are within 5% of the best and the depth transpiled circuit is smaller
            if (abs(averages[best] - averages[i]) / ((float(averages[best]) + float(averages[i]))/2 )*100) <= 10 and int(df["tqc" + str(i) + "Depth"]) < int(df["tqc" + str(best) + "Depth"]):
                print("switched")
                best = i

    return best


#Delete when making into package
qc = QuantumCircuit(5)
qc.x(0)
qc.x(0)
qc.h(4)
qc.y(1)
qc.h(0)
qc.x(4)
qc.cx(1, 3)
qc.x(4)
qc.y(1)
qc.h(0)



oLevel = selector(qc)
print("Chosen opt level: ", oLevel)


# # TEST CODE
# realTimes = []
# depths = []
# time0 = time.time()

# start_time = time.time()
# tqc =  transpile(qc, backend, optimization_level = 0)
# t0 = time.time() - start_time
# df = QCtoDF(tqc)
# job = execute(tqc, backend=backend)
# job_monitor(job)
# result = job.result()
# depths.append(depthFinder(df))
# t1 = result.time_taken
# realTimes.append(t1+t0)

# start_time = time.time()
# tqc =  transpile(qc, backend, optimization_level = 1)
# t0 = time.time() - start_time
# df = QCtoDF(tqc)
# job = execute(tqc, backend=backend)
# job_monitor(job)
# result = job.result()
# depths.append(depthFinder(df))
# t1 = result.time_taken
# realTimes.append(t1+t0)

# start_time = time.time()
# tqc =  transpile(qc, backend, optimization_level = 2)
# t0 = time.time() - start_time
# df = QCtoDF(tqc)
# job = execute(tqc, backend=backend)
# job_monitor(job)
# result = job.result()
# depths.append(depthFinder(df))
# t1 = result.time_taken
# realTimes.append(t1+t0)

# start_time = time.time()
# tqc =  transpile(qc, backend, optimization_level = 3)
# t0 = time.time() - start_time
# df = QCtoDF(tqc)
# job = execute(tqc, backend=backend)
# job_monitor(job)
# result = job.result()
# depths.append(depthFinder(df))
# t1 = result.time_taken
# realTimes.append(t1+t0)

# time1 = time.time()
# generateTime = time1-time0
# print("Actual Times: ", realTimes)

# testBest = realTimes.index(min(realTimes))
# print(testBest)

# for i in range(len(realTimes)):
#     if i != testBest:
#         print(i)
#         print((abs(realTimes[testBest] - realTimes[i]) / ((float(realTimes[testBest]) + float(realTimes[i]))/2 )*100))
#         print(depths[i], depths[testBest])
#         if (abs(realTimes[testBest] - realTimes[i]) / ((float(realTimes[testBest]) + float(realTimes[i]))/2 )*100) <= 10 and depths[i] < depths[testBest]:
#                 print("switched")
#                 testBest = i

# print("Chosen test opt level: ", testBest)



# print("Read Method is faster by: ", (abs(readTime - generateTime)/((readTime + generateTime)/2))*100)
