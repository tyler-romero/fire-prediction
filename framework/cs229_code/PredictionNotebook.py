
# coding: utf-8

# In[121]:

import pandas as pd
import numpy as np
import datetime as dt
import math
data = pd.read_csv('data/incidents2009.csv', dtype ={'Call_Category':str, 'Master_Incident_Number':str, 'Jurisdiction':str, 'Problem':str, 'Street_Block':str, 'Cross_Street':str, 'City':str, 'Postal_Code':str, 'PhonePickUp':str, 'Time_First_Staged_Arrived':str, 'Total_Response_Time':str})


# In[122]:

data['PhonePickUp'] = data['PhonePickUp'].apply(lambda x: dt.datetime.strptime(x,"%m/%d/%y %H:%M:%S"))
#data['Time_First_Staged_Arrived'] = data['Time_First_Staged_Arrived'].apply(lambda x:dt.datetime.strptime(x,"%m/%d/%y %H:%M:%S"))


# In[124]:

zipcode_data = data[(data['Postal_Code'] != "NaN")]
badCodes = set(["NaN","nan","-92103","C92101","U","`92101"])
zipcodes = set(zipcode_data['Postal_Code']).difference(badCodes)


# In[130]:

zipcode_data['Hour'] = zipcode_data["PhonePickUp"].apply(lambda x: x.hour)
zipcode_data['Day'] = zipcode_data["PhonePickUp"].apply(lambda x: x.day)
zipcode_data['Month'] = zipcode_data["PhonePickUp"].apply(lambda x: x.month)


# In[131]:

zipcode_data


# In[171]:

from calendar import monthrange
num_incidents = {}
year = 2009
hourly_by_zip = [["Zipcode","Month","Day","Hour","NumIncidents"]]
for zcode in zipcodes:
    print zcode
    zdata = zipcode_data[(zipcode_data['Postal_Code'] == zcode)]
    num_incidents[zcode] = len(zdata)
    for mn in range(1,13):
        numDays = monthrange(year, mn)[1]
        for dy in range(1,numDays+1):
            for hr in range(24):
                val = len(zdata[(zdata['Hour'] == hr) & (zdata['Month'] == mn) & (zdata['Day'] == dy)])
                hourly_by_zip.append([zcode,mn,dy,hr,val])


# In[172]:

headers = hourly_by_zip.pop(0)
testData = pd.DataFrame(hourly_by_zip, columns = headers)
#testData['date'] = testData['PhonePickUp'].apply(lambda x: dt.datetime.strptime(x,"%m/%d/%y %H:%M:%S"))
testData


# In[189]:

testData['Date'] = testData[['Month','Day','Hour']].apply(lambda x: dt.datetime(2009,x[0],x[1],x[2]),axis=1)


# In[233]:

import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')
f, axes = plt.subplots(7, sharex=True, sharey=False, figsize=(5, 15))
for i in range(1,8):
    d = testData[(testData['Zipcode'] == '92101') & (testData['Month'] == 1) & (testData['Day'] == i)]
    axes[i-1].plot(d['NumIncidents'],d['Date'])


# In[ ]:



