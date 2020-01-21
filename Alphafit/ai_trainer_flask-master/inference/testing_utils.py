import sys

sys.path.append('../data')
sys.path.append('..')
sys.path.append('../inference')

import numpy as np
#import squat_separation as ss

#from sklearn import cross_validation
from sklearn import metrics
import random

#=====[ Returns margin on a prediction for a given data example ]=====
def predictProbs(X,y,X_test, clf_class, **kwargs):
    clf = clf_class(**kwargs)
    clf.fit(X ,y)
    return clf.predict_proba(X_test)

#=====[ Returns labels for a given data example to predict]=====
def predict_labels(X, y, X_test, clf_class, **kwargs):
    clf = clf_class(**kwargs)
    try: 
        clf.fit(X ,y)
    except:
        return []
    return clf.predict(X_test)

#=====[ Prints TP, FP, TN, TN and returns F-score ]=====
def print_analysis(counts, verbose=True):
    try:
        TN = float(counts['0_0'])
        FN = float(counts['1_0'])+ float(counts['-1_0'])
        TP = float(counts['1_1']) + float(counts['-1_-1'])
        FP = float(counts['0_1'])+ float(counts['0_-1']) + float(counts['-1_1']) + float(counts['1_-1'])
        F = 2*TP/(2*TP+FP+FN)
        if(verbose):
            print('Precision: %f' % (TP/(TP+FP)))
            print('Recall: %f' % (TP/(TP+FN)))
            print('F-score: %f\n\n' % F)
        return F
    except Exception as e:
        print(e)

#=====[ Populates TP, FP, TN, FN dictionary for a classification run ]=====
def evaluate(labels, y_test, y_pred):
    if len(y_test) != len (y_pred):
        return 0
    for index, y in enumerate(y_test):
    
        if y_pred[index] == y:
            if y == 1:
                labels['1_1'] +=1
            elif y == 0:
                labels['0_0'] +=1
            elif y == -1:
                labels['-1_-1'] +=1
        elif y == 1:
            if y_pred[index] == 0:
                labels['1_0'] += 1
            if y_pred[index] == -1:
                labels['1_-1'] += 1
        elif y == 0:
            if y_pred[index] == -1:
                labels['0_-1'] += 1
            elif y_pred[index] == 1:
                labels['0_1'] += 1
        elif y == -1:
            if y_pred[index] == 0:
                labels['-1_0'] +=1
            elif y_pred[index] == 1:
                labels['-1_1'] += 1
        
    return metrics.accuracy_score(y_test,y_pred)

def coalesce_twos(y):
    y_true = []
    for label in y:
        if label == 2:
            y_true.append(1)
        else:
            y_true.append(label)
    
    return y_true

#=====[ Cross validation while holding out squats for any given individual at a time. This is done to make sure
#=====[ that we don't train on a person's body type and then test on a very similar (often near identical) example ]=====
def rnd_prediction(training_data, labels, file_names, clf_class, toIgnore=None, num_iters=10, **kwargs):
     
    accuracy = 0
    accuracy_train = 0

    #=====[ Randomly leave out one of the files ]======
    names = list(set(file_names))
        
    #=====[ Dictionaries made to keep track of TP, TN, FP, and FNs ]=====
    counts = {'-1_1':0,'-1_-1':0,'-1_0':0,'0_0':0,'0_1':0,'0_-1':0, '1_0':0, '1_-1':0, '1_1':0}
    training_counts = {'-1_1':0,'-1_-1':0,'-1_0':0,'0_0':0,'0_1':0,'0_-1':0, '1_0':0, '1_-1':0, '1_1':0}

    for name in names:
        toIgnore = name

        #=====[ Build training example and label sets ]=====
        X = np.array([x for index, x in enumerate(training_data) if file_names[index] != toIgnore])
        Y = np.array([y for index, y in enumerate(labels) if file_names[index] != toIgnore])

        #=====[ Build test example and label sets ]=====
        X_test = [x for index, x in enumerate(training_data) if file_names[index] == toIgnore]
        y_test = [y for index, y in enumerate(labels) if file_names[index] == toIgnore]

        #=====[ Get accuracy for this particular round]
        local_accuracy = evaluate(counts, y_test, predict_labels(X, Y, X_test, clf_class, **kwargs))
        local_accuracy_train = evaluate(training_counts, Y, predict_labels(X, Y, X, clf_class, **kwargs))

        accuracy += local_accuracy
        accuracy_train += local_accuracy_train

    #=====[ Print stats for training and testing data ]=====
    # print '############ TRAINING DATA ############\n'
    # print 'Accuracy %f' % (accuracy_train/len(names))
    # print_analysis(training_counts), '\n'
    # print '############ TEST DATA ############\n'
    # print 'Accuracy %f' % (accuracy/len(names))
    # print_analysis(counts),'\n\n'
    return print_analysis(counts,verbose=False),(accuracy/len(names))

#=====[ Cross validation while holding out squats for any given individual at a time. This is done to make sure
#=====[ that we don't train on a person's body type and then test on a very similar (often near identical) example.
#=====[ RUNS 20 TRIALS TO SEE RESULTS AS THEY CHANGE WITH RESPECT TO NUMBER OF TRAINING EXAMPLES ]=====
def rnd_prediction_increase_training(training_data, labels, file_names, clf_class, num_slices=20, toIgnore=None, num_iters=10, **kwargs):
    
    num_training_examples = [x*10 for x in range(1,num_slices)]
    
    accuracy = [0 for _ in range(len(num_training_examples))]
    accuracy_train = [0 for _ in range(len(num_training_examples))]
    f_score = []
    f_score_training = []

    #=====[ Randomly leave out one of the files and test on it num_iter times ]======
    names = list(set(file_names))

    for ind, count in enumerate(num_training_examples):
        
        #=====[ Dictionaries made to keep track of TP, TN, FP, and FNs ]=====
        counts = {'-1_1':0,'-1_-1':0,'-1_0':0,'0_0':0,'0_1':0,'0_-1':0, '1_0':0, '1_-1':0, '1_1':0}
        training_counts = {'-1_1':0,'-1_-1':0,'-1_0':0,'0_0':0,'0_1':0,'0_-1':0, '1_0':0, '1_-1':0, '1_1':0}

        for name in names:
            toIgnore = name
            
            #=====[ Build training example and label sets ]=====
            X = np.array([x for index, x in enumerate(training_data) if file_names[index] != toIgnore])
            Y = np.array([y for index, y in enumerate(labels) if file_names[index] != toIgnore])
        
            #=====[ Build test example and label sets ]=====
            X_test = [x for index, x in enumerate(training_data) if file_names[index] == toIgnore]
            y_test = [y for index, y in enumerate(labels) if file_names[index] == toIgnore]
        
            #=====[ Sample from our training example and label sets ]======
            random.seed()
            indices = random.sample(list(range(len(X))),count)
            X_new = X[indices]
            Y_new = Y[indices]
        
            #=====[ Get accuracy for this particular round]
            local_accuracy = evaluate(counts, y_test, predict_labels(X_new, Y_new, X_test, clf_class, **kwargs))
            local_accuracy_train = evaluate(training_counts, Y_new, predict_labels(X_new, Y_new, X_new, clf_class, **kwargs))

            accuracy[ind] += local_accuracy
            accuracy_train[ind] += local_accuracy_train
        
        #=====[ Average accuracies and store counts for TP, TN, FP, and FNs ]=====
        accuracy[ind]/=len(names)
        accuracy_train[ind]/=len(names)
        f_score.append(print_analysis(counts, verbose=False))
        f_score_training.append(print_analysis(training_counts, verbose=False))
        
    return f_score, f_score_training, accuracy, accuracy_train


def forward_search(num_features, X, Y, file_names, clf_class, **kwargs):
    
    #=====[ Keeps track of best global accuracy and fscore ]======
    best_accuracy = 0
    best_fscore = 0 
    
    #=====[ Builds new feature vector and returns indices of best features to use ]=====
    X_new = X[:,0:0]
    indices = []
        
    for feature in range(num_features):

        #=====[ Used to make sure we have not found a maximum in our accuracy/fscore ]======
        feature_added = False
        
        #=====[ Loops through every feature in X to find the next best feature ]=====
        for index in range(X.shape[1]):
                
            X_temp = np.concatenate([X_new,X[:,index:(index+1)]],axis=1)
            
            fscore, accuracy = tu.rnd_prediction(X_temp,Y,file_names,clf_class,**kwargs)

            #=====[ Checks mean square error between accuracy and f_score ]=====
            if ((1-accuracy)**2 + (1-fscore)**2) < ((1-best_accuracy)**2 + (1-best_fscore)**2):
                best_accuracy = accuracy
                best_fscore = fscore
                best_index = index
                feature_added = True

        if feature_added:
            indices.append(best_index)
            X_new = np.concatenate([X_new,X[:,best_index:(best_index+1)]],axis=1)
        else:
            break
    
    #=====[ Print stats and return indices of top features ]=====
    print("Best accuracy:", best_accuracy)
    print("Best f-score:", best_fscore)
    return indices           