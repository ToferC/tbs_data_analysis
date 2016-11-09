# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 08:37:42 2015

@author: Owner
"""

import pandas as pd
dp = r'/Users/Owner/Documents/Work_transfer/Data/Report Card/'


df1 = pd.read_csv(dp+'BP2020 Department Count.csv')
df2 = pd.read_csv(dp+'Gazorpazorp.csv')

df = pd.merge(df1, df2, how='outer', on='Department')

df['Percentage of Group'] = df['Number']/5173*100
df['Percentage of Network'] = df['Registered']/71335*100

df = df.dropna(how = 'any')
df['Differences in Percent'] = df['Percentage of Group'] - df['Percentage of Network']

info = df.describe()