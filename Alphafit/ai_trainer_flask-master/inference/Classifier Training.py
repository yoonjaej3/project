#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

sys.path.append('../data')
sys.path.append('..')
sys.path.append('../inference')
sys.path.append('../feedback')

from ai_trainer import PersonalTrainer
#import squat_separation as ss
import pickle
import os
import utils as ut

#import classification
import classification_ftopt

#get_ipython().run_line_magic('matplotlib', 'inline')


# #Train Classifiers

# In[ ]:


pt = PersonalTrainer({'squat': 'NeckY', 'pushup': 'NeckY'})

try:
    #pt.load_reps('squat',os.path.join('../data/data_sets','multipleClass4.p'))
    pt.load_reps('pushup',os.path.join('../data/data_sets','pushupDataSet109.p'))
#     pt.load_reps(os.path.join('../data/data_sets','pushupDataSet109.p'))
    ut.print_success('Training data loaded')
    try:
        #pt.set_classifiers('squat',classification_ftopt.train_squat_classifiers(pt))
        pt.set_classifiers('pushup', classification_ftopt.train_pushup_classifiers(pt))
#         pt.set_classifiers(classification.train_pushup_classifiers(pt))
        ut.print_success('Classifiers trained')
    except Exception as e:
        ut.print_failure('Could not train classifiers' + str(e))
except Exception as e:
    ut.print_failure('Could not load training data:' + str(e))


# #Store Classifiers

# In[ ]:

#
# classifiers = pt.get_classifiers('squat')
# pickle.dump(classifiers,open('squat_classifiers_ftopt.p','wb'))

classifiers = pt.get_classifiers('pushup')
pickle.dump(classifiers,open('pushup_classifiers_ftopt.p','wb'))


# In[ ]:




