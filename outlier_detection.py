'''
Created on 25 mars 2021

This program finds outliers in multivariative time series.

@author: Bahareh Afshinpour

'''

from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
from sklearn.ensemble import IsolationForest
import numpy as np
import matplotlib.pyplot as plt
import json
import time 
import datetime
from sklearn.neighbors import LocalOutlierFactor
from numpy import save


def process_time_format(timeInString):
    ''' 
    We assume that time is already in seconds.
    If timestamps have different format, 
    this function should convert them to seconds
    '''
    timeInSecond = timeInString
    return timeInSecond


def outlier_detection(file, filename_prefix, category, metrics):
    '''
    file: input file containing the input dataset in json format.
    filename_prefix: used to determine the prefix of the filenames where the outputs are stored. 
    category: name of the category of the metrics (used to retrieve metrics values in json input file)
    metrics: list of metrics used to retrieve desired values from the json input file. 
    
    '''
    print("Start finding outliter in {} data containing {} metrics".format(category, metrics))
    with open("./data/"+file, 'r') as f:
            monitoringDataset = json.load(f)


    mProcessFrom = 0 
    mProcessTo = 0  

    startTime = monitoringDataset[0]["timestamp"]
    stopTime = monitoringDataset[-1]["timestamp"]
    valueArray = [] # Keeps all extracted values 
    timeArray = []  # Keeps all time indices corressponding to valueArray
    found_entries = 0
    # i is time index 
    for i in range(startTime,stopTime): 
        ''' 
        This main loop, enumerate time from startTime to stopTime in iterator i, 
        and find index of elements that have timestamp i, then merge them in temp array and append it to 
        '''
        ######################## Processing Monitoring #######################
        # find the first Monitoring element happned on the timestamp ( i )
        for k in range(0 ,len(monitoringDataset)): # Search all elements in monitoring json file
            found_the_last_entry = 0 
            s = monitoringDataset[k]["timestamp"]
            T = process_time_format(s)
            if (i < T): # We just passed timestamp i, so we exit from searching
                found_entries = 0   
                break;
            if(T == i): # We just found a new element with timetamp i, so we add it.
                found_entries = 1 # We found at least one elemnt with timestamp i
                mProcessFrom = k # The index of the first element with timestamp i is saved in mProcessFrom to be used later
                
                for w in range(mProcessFrom,len(monitoringDataset)): # We go to find all elements with timestamp i
                    s = monitoringDataset[w]["timestamp"]
                    T = process_time_format(s)

                    if(T > i): # If the element monitoringDataset[w] has timestamps greater than i, we exit searching
                        found_the_last_entry = 1
                        mProcessTo = w # The index of the last element with timestamp i is saved in mProcessTo to be used later
                        break; # find the first element happened after the timestamp ( i ). Now we know the first and the last elements with time stamp i
                    if(T < i): # We assume that the element have chronological order. This should not be happened that we find a new element with a past timestamp 
                        raw_input("Time anomaly, an entry with an older time found! ...")
                        break;
                if (found_the_last_entry): # exit flag 
                    break;
        if(found_entries == 0):
            continue;
        else:
            found_entries = 0
                
        temp = [None for init in range(len(metrics))]
        s = ""

        foundMetric =0 # If foundMetric=0 in the end, we havenot found any metric for the bench  
        # ditinguish tagets and write each one on its column
        new_found_metricmonitoring = []

        for met in range(len(metrics)):
            metric = metrics[met].lower()
            for d in range(mProcessFrom,mProcessTo): # Search monitoringDataset to see if we can find met metric between mProcessFrom,mProcessTo indices 
                # print(monitoringDataset[d])
                s = monitoringDataset[d]["timestamp"]
                timestamp = process_time_format(s)
                
                # For user info, just check if this metric is seen for the first time and does not exist in the metrics list
                if ((category.lower()  == monitoringDataset[d]["category"].lower()) and (monitoringDataset[d]["metric"].lower() not in metrics)):
                    if( monitoringDataset[d]["metric"].lower() not in new_found_metricmonitoring):
                        print("new metric found!!!!!: " + monitoringDataset[d]["metric"])
                        new_found_metricmonitoring.append(monitoringDataset[d]["metric"].lower())
                        
                        
                if (timestamp == i): # if time is correct
                    if(monitoringDataset[d]["metric"].lower() == metric.lower() and category.lower()  == monitoringDataset[d]["category"].lower()):
                        temp[met] = monitoringDataset[d]["value"]
                        foundMetric =1
                        # print(monitoringDataset[d]["value"])
                else:
                    print("Time mismatch")


        if(foundMetric):
            if(None in temp):
                print("One (or more) metrics does not have value: {} at {}".format(repr(temp),s))
            valueArray.append(temp)
            timeArray.append(timestamp)
            # print(valueArray)
            mProcessFrom = mProcessTo   


    # saving extracted value array and its timestamps
    np.save("./saves/"+filename_prefix+ '_valueArray-'+ category.lower()+'.npy', valueArray)
    np.save("./saves/"+filename_prefix+ '_timeArray-'+ category.lower()+'.npy', timeArray)

    #*******************************************************************
    X = np.array(valueArray,dtype=np.float64)
    clf_LOF = LocalOutlierFactor(n_neighbors=2,algorithm='auto',metric='minkowski')
    #'euclidean','manhattan',novelty
    clf_IF = IsolationForest(random_state=0).fit(X)
    A_LOF=clf_LOF.fit_predict(X)
    A_IF =clf_IF.fit_predict(X)
    unique_LOF, counts_LOF = np.unique(A_LOF, return_counts=True)
    unique_IF, counts_IF = np.unique(A_IF, return_counts=True)
    #****************************** Anomaly index *********
    Anomaly_index_LOF=[]
    Anomaly_index_IF=[]
    monitoring_value=[]
       
    for i in range(len(A_LOF)):
        if A_LOF[i]==-1:
            Anomaly_index_LOF.append(i)
    for i in range(len(A_IF)):
        if A_IF[i]==-1:
            Anomaly_index_IF.append(i)
    
    outliers = []
    for d in Anomaly_index_LOF:
        x = timeArray[d]
        timestamp = process_time_format(x)
        outliers.append(timestamp)
    for d in Anomaly_index_IF:
        x = timeArray[d]
        timestamp = process_time_format(x)
        outliers.append(timestamp)
    
    np.save("./saves/"+filename_prefix+ '_outliers_'+ category.lower()+'.npy', outliers)
    pos = [i for i in range(len(X))]
    plt.figure()

    for j in range(len(metrics)):
        plt.subplot(len(metrics),1,(j+1))
        plt.subplots_adjust(hspace = .1)
        monitoring_value=[]
        for i in range(len(X)):
            monitoring_value.append(X[i][j])
        plt.plot(pos,monitoring_value, 'c',linewidth=0.5)
        for i in range(len(Anomaly_index_IF)):
            plt.axvline(x=Anomaly_index_IF[i], ymin=-0.5, ymax=0.1,color = 'r')

        for i in range(len(Anomaly_index_LOF)):
            plt.axvline(x=Anomaly_index_LOF[i], ymin=-0.5, ymax=0.1)
        plt.title(metrics[j],y=0.1, fontsize=7)
        
    plt.tight_layout()  
    plt.savefig("./pdf/"+filename_prefix+ '_outliers_monitoring_stats-'+ category+'.pdf',dpi=600)
    plt.close()
    return 1



