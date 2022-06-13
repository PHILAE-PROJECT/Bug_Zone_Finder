# The Bug-Zone Finder

Testing and fault processing on a wide variety of network-enabled embedded systems have some complexities derived from a large amount of communicated data and low resources on the device. Embedded devices such as network appliances(internet boxes, network routers), cyber-physical and IoT devices (Internet TV, Wearable health monitors, smart home security systems) even cell phones generally communicate or relay a large amount of data received and transferred from/to multiple remote machines, while there are not enough storage and processing resources on the device to record debugging information (log files and exchange package, etc.). It is challenging to find a fault and associate it with the proper network request that caused it. Operators and analyzers always need to find periods, in which, the systems enter in an anomalous status. In this project, we determine the Bug-Zone areas on the monitoring log file.

## What is the Bug-Zone:

Bug-Zone is a time period, in which, the number of anomalies is more than a threshold. Bug-Zones help us to filter false positives and identify temporal changes in the device behavior trends.

## Usage
To run the tool, simply type in Linux: 
```python
python3 main.py
```

- config file: 
In the config file, some parameters can be set. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Monitoring window. On each timestamp, we counted all the outliers within a specific window to find bug zones. The size of this window specifies in this parameter.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Files: name of input files containing monitoring data. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Bug_zone_threshold: a float number that determines a threshold and the outlier density above it consider a bug zone. 
 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Categories and Metrics: Metrics are classified into different categories. All the metrics in categories are processed together to find outliers. 

- data files: data files in JSON format should be placed in the "data" folder. Each entry should have the following information:
```JSON
    {
        "timestamp": x,
        "category": "xyz",
        "metric": "abcd",
        "value": m
    }    
```

- **Fresh outlier** and **Fresh bug zones** in main.py: These two flags makes the tool process the data from the input files (fresh) or reuse the stored outlier results  


