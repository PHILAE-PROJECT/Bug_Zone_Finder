'''
Created on 25 mars 2021

This program read outliers from npy files and finds Bug-Zones.


@author: Bahareh Afshinpour

'''

from tempfile import TemporaryFile
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
from sklearn.ensemble import IsolationForest
import numpy as np
import matplotlib.pyplot as plt
import json
import time 
import datetime
import math 
from scipy.signal import savgol_filter

def bugzone_calc( window_size_monitoring,filename_prefix, categories, threshold ):

    print("############################  Finding Bug Zones ###############################")
    print(repr(categories))
    outliers = []
    count_weighted_outliers_in_window_monitoring=[]
    # Read each category's outlier file
    for cat in categories:
            print("Openning "+cat)
            outliers.append( np.load("./saves/"+filename_prefix+ '_outliers_'+ cat.lower()+'.npy'))
        
    # Calculate weight of outliers 1/sqrt(len)
    outliers_weight = []
    for d in outliers:
        if (len(d)):
            outliers_weight.append(1.0/math.sqrt(len(d)))
        else:
            outliers_weight.append(0)
    
    def getCount(outlier_index, time_index, window): 
    
        'Returns the count of elements in list that satisfies the given condition'
        count = 0
        for i in range(len(outliers[outlier_index])):
            if(outliers[outlier_index][i] >= time_index-window/2 and outliers[outlier_index][i] <= time_index+window/2):
                count += 1
            elif(outliers[outlier_index][i] > time_index+window/2):
                break

        return count   
    
    # count number of outliers in each window. result --> count_weighted_outliers_in_window_monitoring
    count_weighted_outliers_in_window_monitoring = []
    for i in range ( max(map(max,outliers))): # Continue until the max time of outliers --> max(map(max(X)))
        total_weight =0
        for j in range(len(outliers)):
            if (outliers_weight[j]):
                total_weight+= getCount(j,i,window_size_monitoring) * outliers_weight[j]
        count_weighted_outliers_in_window_monitoring.append(total_weight)

    ############################################################ Normalize / Standardize
    from sklearn import preprocessing
    count_weighted_outliers_in_window_monitoring_norm = []
    np_monit_outliers = np.array(count_weighted_outliers_in_window_monitoring).reshape(-1, 1)
    scaler = preprocessing.StandardScaler().fit(np_monit_outliers)
    count_weighted_outliers_in_window_monitoring_norm = scaler.transform(np_monit_outliers).reshape(1,-1)[0]


    ########################################################## Save 
    np.save("./saves/"+filename_prefix+ '_count_weighted_outliers_in_window_monitoring_norm.npy', count_weighted_outliers_in_window_monitoring_norm)
           
    ########################################################## Plotting

    if(count_weighted_outliers_in_window_monitoring_norm.any()): 
        bugzone_flag =0 
        monitoring_bugzones = []
        bz_start =0         
        print(repr(monitoring_bugzones))
        for i in range (len(count_weighted_outliers_in_window_monitoring_norm)):
            if(count_weighted_outliers_in_window_monitoring_norm[i]> threshold):
                if(bugzone_flag):
                    continue;
                else:
                    bugzone_flag = 1
                    bz_start = i
            else:
                if(bugzone_flag):
                    monitoring_bugzones.append([bz_start, i])
                    bugzone_flag = 0
                else:
                    continue
        
        np.save("./saves/"+filename_prefix+ '_bugzones_monitoring.npy',monitoring_bugzones)
        plt.figure()
        def get_cmap(n, name='hsv'):
            '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
            RGB color; te keyword argument name must be a standard mpl colormap name.'''
            return plt.cm.get_cmap(name, n)         
        cmap = get_cmap(len(outliers))
        outlier_names = list(categories)
        for i,d in enumerate(outliers):# i :  index outlier, d array of seconds of the outlier  happen in a day
            for second in d:

                plt.scatter(second, 2.55+((2.0*i)/len(outliers)), c=np.array([cmap(i)]),s=0.1)
            plt.text(-0.5, 2.6+((2.0*i)/len(outliers)), outlier_names[i]+"(weight:{:.2f})".format(outliers_weight[i]) , ha='left',fontsize='xx-small')
         
         
        plt.plot(range(len(count_weighted_outliers_in_window_monitoring)), count_weighted_outliers_in_window_monitoring,linewidth=0.5,label="Raw  outlier density")
        
        plt.plot(range(len(count_weighted_outliers_in_window_monitoring_norm)), count_weighted_outliers_in_window_monitoring_norm,linewidth=0.5,label="Standardized outlier density")
        plt.legend()
        plt.plot([1,len(count_weighted_outliers_in_window_monitoring_norm)-1], [threshold,threshold],linewidth=0.5)
        plt.legend()
        plt.savefig("./pdf/"+filename_prefix+ '_monitoring_bugzone.pdf',dpi=600)
       
        print("Monitoring bug zones written successfully.")     

    else: 
        print("Monitoring outliers array is empty.")

    
    plt.close()

   