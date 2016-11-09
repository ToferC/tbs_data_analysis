# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 09:14:57 2015

@author: Owner
"""

import pandas as pd
from datetime import datetime
#%% The goal is to annotate this analysis as completely as possible
data_path = r'/Users/Owner/Documents/Work_transfer/Data/Report Card/'
df = pd.read_excel(data_path+'comments.xlsx')
#%%
#The ultimate goal for this file is to isolate collaboration on the network
#Based on the group that the collaboration is in
#I have a dataset that contains the amount all the comments in the network and
#It has a bunch of excess data. let's get rid of that.

df.drop('value type', 1, inplace=True)
df.drop('access id', 1, inplace=True)
df.drop ('enabled',1 , inplace=True)

#%%
#Let's turn that Unix Timestamp into some actual dates for humans
#This is slowly killing me, maybe I'll do it later
#df = df.dropna(0, subset=['time created'], how='all')
#df['time created'] = df['time created'].astype(float)
#df['time created'] = pd.to_datetime(df['time created'], unit='ns')

