#!/usr/bin/env python
# coding: utf-8

# In[1]:


from qiskit import *
from qiskit.visualization import plot_bloch_multivector, plot_histogram, array_to_latex
import itertools
import numpy as np
from time import sleep
import pandas as pd
#import progressbar
import csv
sim = Aer.get_backend('qasm_simulator')
get_ipython().run_line_magic('matplotlib', 'inline')


# ## Find all permutations and synonyms

# In[2]:


gates = ['x', 'y', 'z', 'h']
gateCombos = []
comboSV = []
similar = []


# In[3]:


#Find all permutations and append their statevectors and permutations to lists
for L in range(1, len(gates)+1):
    
    #for subset in itertools.permutations(gates, L):
    for subset in itertools.product(gates, repeat=L):
        #print(subset)
        gateCombos.append(subset)
#Add a no gate option
gateCombos.append('')
        
#find statevectors of each possible permutation and store in list
for i in range(len(gateCombos)):
    qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
    #print(gateCombos[i])
    
    for j in gateCombos[i]:
        getattr(qc , j)(0)
        #print(qc)
    # Let's get the result:
    qc.save_statevector()
    qobj = assemble(qc)
    result = sim.run(qobj).result()
    # Print the statevector neatly:
    final_state = result.get_statevector()
    array_to_latex(final_state, prefix="\\text{Statevector = }")
    comboSV.append(final_state)


# In[4]:


len(gateCombos)
print(gateCombos[len(gateCombos)-1])


# In[5]:


len(comboSV)
print(comboSV[len(comboSV)-1])


# In[6]:


#Create a list of synonym pairs based on if statevectors are equal
#bar = progressbar.ProgressBar(maxval=len(comboSV)).start()
for i in range(len(comboSV)):
    for j in range(len(comboSV)):
        temp = []
        if(i != j and comboSV[i]==comboSV[j]):
            temp.append(gateCombos[i])
            temp.append(gateCombos[j])
            #print(temp)
            similar.append(temp)
    #bar.update(i)
            


# In[7]:


len(similar)


# In[8]:


#bar = progressbar.ProgressBar(maxval=len(similar)).start()
# provider = IBMQ.get_provider('ibm-q')
# backend = provider.get_backend('ibmq_armonk')
#sort largest synonym in pair first
#If synonyms are the same in length, check computing times of each and set slower one as target and quicker one as the replacement
listToRemove = []
for i in range(len(similar)):
    if len(similar[i][1]) > len(similar[i][0]):
        similar[i].insert(0, similar[i].pop(1))
    elif len(similar[i][1]) == len(similar[i][0]):
        #1
        #Commented out sections of code are for usage with real QHardware
        qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
        for j in similar[i][0]:
            getattr(qc , j)(0)
        qc.measure(0, 0)
        result = execute(qc, backend=sim, shots = 1000).result()
        # job = execute(qc, backend=backend)
        # job_monitor(job)
        # result = job.result()
        time1 = result.time_taken
        #2
        qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
        for j in similar[i][1]:
            getattr(qc , j)(0)
        qc.measure(0, 0)
        result = execute(qc, backend=sim, shots = 1000).result()
        # job = execute(qc, backend=backend)
        # job_monitor(job)
        # result = job.result()
        time2 = result.time_taken
        if time2 > time1:
            similar[i].insert(0, similar[i].pop(1))
        if time2 == time1:
            listToRemove.append(i)
    #bar.update(i)
listToRemove.sort(reverse=True)
#print("Removing Elements at Indices: " + str(listToRemove))
listToRemove.sort(reverse=True)
for r in listToRemove:
    similar.pop(r)


# In[9]:


len(similar)


# ## Create Database File

# In[10]:


with open(r"Synonym_Database\key.csv", 'w', newline='', encoding='UTF8') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(['Target', 'Replacement'])
    writer.writerows(similar)


# ### CSV to Pandas DF

# In[11]:


df = pd.read_csv(r"Synonym_Database\key.csv")


# ### Filtering out multiple replacements for one target

# In[12]:


unique = df['Target'].unique()
unique = unique.tolist()
targets = df['Target'].tolist()


# In[13]:


bar = progressbar.ProgressBar(maxval=len(unique)).start()
remove = []
for i in range(len(unique)):
    bar.update(i)
    times = []
    indices = []
    for j in range(len(targets)):
        if unique[i] == targets[j]:
            indices.append(j)
    for x in range(len(indices)):
        #Commented out sections of code are for usage with real QHardware
        qc = QuantumCircuit(1, 1) #1 quantum, 1 classical
        for q in similar[x][1]:
            getattr(qc , q)(0)
        qc.measure(0, 0)
        result = execute(qc, backend=sim, shots = 1000).result()
        # job = execute(qc, backend=backend)
        # job_monitor(job)
        # result = job.result()
        times.append(result.time_taken)
    least = min(times)
    for e in indices:
        remove.append(e)
    remove.remove(indices[times.index(least)])
remove.sort(reverse=True)
#print(remove)
for i in remove:
    similar.pop(i)


# In[14]:


len(similar)


# In[15]:


with open(r"Synonym_Database\key.csv", 'w', newline='', encoding='UTF8') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(['Target', 'Replacement'])
    writer.writerows(similar)


# ## Reading and Cleaning File

# In[16]:


#Get simplist replacements for each target
keyDF = pd.read_csv(r"Synonym_Database\key.csv")

for item in range(len(keyDF)):
    for m in range(0, 50):
        for element in range(len(keyDF)):
            if keyDF['Target'][element] == keyDF['Replacement'][item]:
                # print("1. " + str(keyDF['Replacement'][item]))
                # print("2. " + str(keyDF['Target'][element]))
                keyDF['Replacement'][item] = keyDF['Replacement'][element]

lst = []
#print(keyDF)
for i in range(len(keyDF)):
    temp = []
    temp.append(keyDF['Target'][i])
    temp.append(keyDF['Replacement'][i])
    lst.append(temp)
with open(r"Synonym_Database\key.csv", 'w', newline='', encoding='UTF8') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(['Target', 'Replacement'])
    writer.writerows(lst)


# In[17]:


#For every replacement item(j), search for j as a target and set j as a target's replacement = j
#repeat this action on j until it is no longer found as a target

