'''
Created on 25 mars 2021

This is the main program of Bug-Zone identifier.
It calls outlier_detection to find anomalies in 
mulitvariative series then calls bug_zone_finder to find Bug-Zones. 
A Bug-Zone is a time period, in which, the number 
of anomalies in a time window is greater than a threshold value.

@author: Bahareh Afshinpour

'''

import json
import sys
import numpy as np
from outlier_detection import outlier_detection
from bug_zone_finder import bugzone_calc
# 0: Read outliers from previously processed information. 
# 1: Read outliers from the input file
fresh_outliers = 1 
# 0: Only plot bugzones from preivously calculated bug zones
# 1: Calculate and plot bug zones from scratch
fresh_bug_zone = 1

with open("config.json", 'r') as f:
        config = json.load(f)
window_monitoring = config[0]["window-monitoring"]
files = config[0]["files"].split(",")
bz_threshold = config[0]["bug_zone_threshold"]
metric_categories = config[0]["Mertics"]
			
for cat,m in metric_categories.items():
    print(cat)
for file in files:
    print("####################################\r\nStart processing " + file + "\r\n############################################")
    filename_prefix = file + "_" + str(window_monitoring)
    for cat,metrics in metric_categories.items():
        # print(metric_categories.keys())
        status  = outlier_detection(file, filename_prefix, cat, metrics)
    bugzone_calc(window_monitoring,filename_prefix, metric_categories.keys(), bz_threshold )

sys.exit()
