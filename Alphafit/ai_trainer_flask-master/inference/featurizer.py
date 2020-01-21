import numpy as np
import math
from collections import defaultdict

import numpy as np
from sklearn import preprocessing


#======[ Returns index to frame with minimum y-coord for specified key ]=====
def get_min(squat,key):   
    
    #=====[ Return max because of inverse frame of reference of kinect ]=====
    return max([(coord,index) for index, coord in enumerate(squat[key])])[1]

#=====[ Returns index to frame with y-coord closes to the midpoint between start/end and squat position for specified key ]=====
def get_midpoint(squat,start,key, multiple):
    
    #=====[ Decide whether getting midpoint between start and squat or squat and end ]=====
    if start:
        start = 1
        end = get_min(squat,key)
    else:
        start = get_min(squat,key)
        end = squat.shape[0] - 1
        
    #=====[ Uses the 'true_mid' as an evaluation metric to find optimal index  ]=====
    true_mid = (squat.iloc[end][key] - squat.iloc[start][key])*multiple
    deltas = [(np.abs(true_mid - (squat.iloc[end][key] - squat.iloc[index][key])), index) for index in range(start,end)]
    try: 
        return min(deltas)[1]
    except:
        return start

#=====[ Returns squat at the first position ]=====
def starting_position(squat):
    return squat.iloc[[1]]

#=====[ Returns index to frame with y-coord closes to the midpoint between start and squat position for specified key ]=====
def start_to_squat(squat,key,multiple=0.5):
    return squat.iloc[[get_midpoint(squat,start=1,key=key,multiple=multiple)]]

#=====[ Returns frame with minimum y-coord for specified key ]=====
def squat_position(squat,key):
    return squat.iloc[[get_min(squat,key)]]

#=====[ Returns index to frame with y-coord closes to the midpoint between squat position and end for specified key ]=====
def squat_to_end(squat,key,multiple=0.5):
    return squat.iloc[[get_midpoint(squat,start=0,key=key,multiple=multiple)]]

#=====[ function for plotting full set of 25 coordinates for a given frame ]=====
def plotBody(df):
    coords = np.array(df)
    xs = [coords[0][i] for i in range(0,coords.size) if i % 2 == 0]
    #=====[ Plot -1* coords because of kinect's frame of reference ]=====
    ys = [-1*coords[0][i] for i in range(0,coords.size) if i % 2 == 1]
    plt.plot(xs,ys,linestyle='None',marker='o')
    plt.axis([-60,60,-1.2,0.2])

#=====[ Returns angle between three specified joints along the two specified axes  ]=====
def get_angle(state, joint1, joint2, joint3, axis1, axis2):

    bone1 = math.sqrt(math.pow(state[joint2 + axis1] - state[joint1 + axis1], 2) + math.pow(state[joint2 + axis2] - state[joint1 + axis2], 2))
    bone2 = math.sqrt(math.pow(state[joint2 + axis1] - state[joint3 + axis1], 2) + math.pow(state[joint2 + axis2] - state[joint3 + axis2], 2))

    #=====[ Gets distance between the disconnected joints  ]=====
    distance = math.sqrt(math.pow(state[joint1 + axis1] - state[joint3 + axis1], 2) + math.pow(state[joint1 + axis2] - state[joint3 + axis2], 2))
    
    try:
        angle = math.acos((math.pow(bone1, 2) + math.pow(bone2, 2) - math.pow(distance, 2)) / (2 * bone1 * bone2))
    except Exception as e:
        print(e)
        return 0

    return angle

#=====[ Returns ratios of changes between two angles over time  ]=====
def get_angle_changes(angle1, angle2):

    assert(len(angle1) == len(angle2))
    
    #=====[ Gets max angle swept  ]=====
    full_angle1 = angle1[-1] - angle1[0]
    full_angle2 = angle2[-1] - angle2[0]
    
    ratios=[]
    
    for time in range(1,len(angle1)):
        ratios.append(abs(((angle1[time] - angle1[time-1]) / full_angle1) - (angle2[time] - angle2[time-1]) / full_angle2))
        
    return ratios

#=====[ Returns states to use for feature extraction  ]=====
def get_states(squat, key, multiples=[0.5]):
    
    states = []
    states.append(starting_position(squat))

    for multiple in multiples:
        states.append(start_to_squat(squat,key,multiple))
        states.append(squat_to_end(squat,key,multiple))

    states.append(squat_position(squat,key))
    
    return states

#=====[ Extracts four basic sets of features for a given squat and concatenates them  ]=====
def extract_basic(squat, key):
    
    return np.concatenate(get_states(squat,key),multiples=[0.5])


#############################################################################################
####### Extracts advanced features for a given squat - ASSUMES Z COORDINATES INCLUDED  ######
#############################################################################################

def get_advanced_feature_vector(squats, key, multiples):
    #=====[ Initialize dict  ]=====
    advanced_feature_vector = defaultdict(list)
    
    #=====[ Extract advanced features for each squat  ]=====
    for squat in squats:
        squat = get_states(squat,key,multiples)
        advanced_feature_vector['stance_width'].append(stance_shoulder_width(squat))
        # advanced_feature_vector['stance_alignment'].append(stance_straightness(squat))
        advanced_feature_vector['knees_over_toes'].append(knees_over_toes(squat))
        advanced_feature_vector['bend_hips_knees'].append(bend_hips_knees(squat))
        advanced_feature_vector['back_straight'].append(back_straight(squat))
        advanced_feature_vector['head_alignment'].append(head_aligned_back(squat))
        advanced_feature_vector['squat_depth'].append(depth(squat))
        advanced_feature_vector['back_hip_angle'].append(back_hip_angle(squat))

    return advanced_feature_vector

#=====[ Takes a feature dictionary and labels and appropriately populates a Y and X with unit variance and zero mean  ]=====
def transform_data(features, labels, toIgnore, predict=False):
    X = {}
    Y = {}

    for feature in features:
        training_data = np.array([training_example for training_example in features[feature]])
    
        #=====[ Try to fit_transform data, print feature name if fail  ]=====
        try:
            if feature not in toIgnore:
                X[feature] = preprocessing.StandardScaler().fit_transform(training_data)
                if not predict:
                    Y[feature] = labels[feature]        
        except Exception as e:
            # print e, feature
            continue;

    return X, Y

#=====[ Extracts features for determining whether feet are shoulder width apart  ]=====
def stance_shoulder_width(states):
   
    #=====[ Checks distance between heels and shoulsers in all frames ]=====
    left_heels_shoulder_apart = [float(state['AnkleLeftX'] - state['ShoulderLeftX']) for state in states]
    right_heels_shoulder_apart = [float(state['AnkleRightX'] - state['ShoulderRightX']) for state in states]
    
    return np.concatenate([left_heels_shoulder_apart, right_heels_shoulder_apart])

#=====[ Extracts features for determining whether shoulders are directly over ankles  ]=====
def stance_straightness(states):
    
    #=====[ Checks to make sure left heels directly under shoulder in all states ]=====
    left_heels_under_shoulder =[float(state['AnkleLeftZ'] - state['ShoulderLeftZ']) for state in states]

    #=====[ Checks to make sure right heels directly under shoulder in all states  ]=====
    right_heels_under_shoulder = [float(state['AnkleRightZ'] - state['ShoulderRightZ']) for state in states]
    return np.concatenate([left_heels_under_shoulder, right_heels_under_shoulder])


#=====[ Extracts features to determine if the knees are going past the toes (and possibly heels lifitng up)  ]=====
def knees_over_toes(states):

    #=====[ Checks to make sure knees are not pushing out over feet  ]=====
    left_feet_flat = [math.pow(state['KneeLeftZ'] - state['AnkleLeftZ'], 2) for state in states]
    right_feet_flat = [math.pow(state['KneeRightZ'] - state['AnkleRightZ'], 2) for state in states]
    
    return np.concatenate([left_feet_flat, right_feet_flat])


#=====[ Extracts features to determine if the hips and knees are simultaneously bending  ]=====
def bend_hips_knees(states):

    #=====[ Gets angles at the knees and hips for the left and right sides of the body  ]=====
    left_bend_knees = [get_angle(state, 'AnkleLeft','KneeLeft','HipLeft','Y','Z') for state in states]
    left_bend_hips = [get_angle(state,'SpineMid','HipLeft','KneeLeft','Y','Z') for state in states]
    right_bend_knees = [get_angle(state,'AnkleRight','KneeRight','HipRight','Y','Z') for state in states]
    right_bend_hips = [get_angle(state,'SpineMid','HipRight','KneeRight','Y','Z') for state in states]

    ratios = np.concatenate([get_angle_changes(left_bend_hips,left_bend_knees),get_angle_changes(right_bend_hips,right_bend_knees)])
    
    return np.concatenate([left_bend_knees, left_bend_hips, right_bend_knees, right_bend_hips, ratios])


#=====[ Extracts features to determine if the back is straight throughout the squat  ]=====
def back_straight(states):

    assert len(states) > 0
    back_angles = [get_angle(state,'SpineBase','SpineMid','SpineShoulder','Y','Z') for state in states]

    #=====[ Gets average and variance  ]=====
    # avg = np.average(back_angles)
    # features = []
    # variance = sum(map(lambda x : (x - avg)**2, back_angles)) / len(back_angles)
    # features.append(variance)
    # features.append(avg)

    return np.array(back_angles)

#=====[ Extracts features to determine if the head and back are aligned  ]=====
def head_aligned_back(states):
    assert len(states) > 0
    head_angles = [get_angle(state,'Head','Neck','SpineShoulder','Y','Z') for state in states]

    #=====[ Gets average and variance  ]=====
    avg = np.average(head_angles)
    features = []
    variance = sum([(x - avg)**2 for x in head_angles]) / len(head_angles)
    features.append(variance)
    features.append(avg)

    return np.array(features)

#=====[ Extracts features to determine if the squat is deep enough  ]=====
def depth(states):

    #=====[ Gets state at bottom of the squat  ]=====
    state = max(states, key=lambda x: float(x['NeckY']))   

    depth_angle = get_angle(state, 'AnkleLeft','KneeLeft','HipLeft','Y','Z')

    return np.array([depth_angle, state['HipLeftY'],state['HipRightY']])

#=====[ Extracts features to determine if the back is appropriately angled at the hip  ]=====
def back_hip_angle(states):

    slopes = []
    
    for state in states:
        slopes.append(abs(float(state['NeckY']) - float(np.average([float(state['HipLeftY']), float(state['HipRightY'])]))) / float(state['NeckZ'] - np.average([float(state['HipLeftZ']), float(state['HipRightZ'])])))
        
    return np.array(slopes)
















