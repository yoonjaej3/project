#!/usr/bin/env python
# coding: utf-8

# #Pipeline for generating a data set from preprocessed reps and labels

# In[1]:


import sys

sys.path.append('../data')
sys.path.append('../inference')
sys.path.append('../')
sys.path.append('../data/squat_coords')

import numpy as np
import pandas as pd
import pickle
import os

#get_ipython().run_line_magic('matplotlib', 'inline')


# #Step 1: Extract Data

# In[2]:


#=====[ Specify directory we wish to pull data from -- choose pushups or squats ]=====
data_dir = '../data/pushup_coords'
#data_dir = '../data/squat_coords'

X = []
file_names = []
ignoreList = []

#=====[ Iterate through every file in the directory ]=====
for f in os.listdir(data_dir):    
    
    #=====[ Check to make sure file is not in ignore list ]=====
    ignore = False
    for toIgnore in ignoreList:
        if toIgnore in f:
            ignore = True
            break
    
    #=====[ Add squat to our X ]=====
    if not ignore:
        reps = pickle.load(open(os.path.join(data_dir, f),'rb'))

        for rep in reps:
            
            #=====[ Check if Squat is tuple of just DataFrame ]=====
            if type(rep) == type((0,0)):
                X.append(rep[0])
            else: 
                X.append(rep)
            
            file_names.append(f)


# #Step 2: Get Labels

# In[3]:


#Import proper labels depending on whether you're using squats or pushups
import pushup_labels2 as labels
#import squat_labels as labels

#=====[ Specify labels corresponding to file names; Must be in alphabetical/numerical order ]=====
label_arrays = [labels.labels12, labels.labels13, labels.labels14, labels.labels16, labels.labels17, labels.labels18, labels.labels19, labels.labels26, labels.labels27, labels.labels28, labels.labels29]

#=====[ Concatenate labels into single label matrix (dataframe) ]=====
Y = np.concatenate(label_arrays)
Y = pd.DataFrame(Y,columns=labels.label_names)


# In[4]:


#=====[ Confirm lengths of necessary parameters ]=====
print(len(X))
print(len(Y))
print(len(file_names))


# #Step 3: Pickle (store) Data Set

# In[5]:


pickle.dump({'X':X,'Y':Y,'file_names':file_names},open('pushupDataSet109.p','wb'))


# In[6]:


data = pickle.load(open('pushupDataSet109.p','rb'))
print(len(data['X']))


# In[ ]:




