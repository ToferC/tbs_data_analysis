# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 13:07:17 2015

@author: Owner
"""

#This script aims to do the following:
# 1. Take a list of all users with their email and registration date
# 2. Classify everybody by their respective departments
# 3. Group amount of users by department every month

import pandas as pd
import os
import csv

data_path = r'/Users/Owner/Documents/Work_transfer/Data/GCconnex/'
key_path = r'/Users/Owner/Documents/Work_transfer/Data/GCconnex/Profile Statistics/'
save_path = r'/Users/Owner/Documents/Work_transfer/Data/Monthly Data Table/December/'

users = pd.read_csv(data_path+'Users.csv',  header=None)

usercol = ['Email', 'Name', 'Time']
users.columns = usercol

users[['User', 'Department']] = users['Email'].str.split('@', expand=True)

users = users[['User', 'Department', 'Time']]
users['Department'] = users['Department'].str.lower()

dept = users.Department
dept_sort = set(dept)
dept_dict = {}

with open(os.path.join(key_path, "csv_keys.csv"), "r") as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)
    
    for row in reader:
        email, acronym = row
        dept_dict[email] = acronym

dept_dict['cadets.gc.ca'] = 'CADETS'
dept_dict['canada.gc.ca'] = 'CANADA'
dept_dict['canada.ca'] = 'CANADA'
dept_dict['tribunal.gc.ca'] = 'TRIBUNAL'
dept_dict['cannor.gc.ca'] = 'CED/DEC'
dept_dict['ci-oic.gc.ca'] = 'CI/OIC'
dept_dict['ccgs-ngcc.gc.ca'] = 'CCGS/NGCC'
dept_dict['god.ccgs-ngcc.gc.ca'] = 'CCGS/NGCC'
dept_dict['clo-ocol.gc.ca'] = 'OCOL/CLO'
dept_dict['csps.gc.ca'] = 'CSPS/EFPC'
dept_dict['interenational.gc.ca'] = 'DFAITD/MAECD'
dept_dict['cnb-ncw.gc.ca'] = 'CNB/NCW'
dept_dict['ncw-cnb.gc.ca'] = 'CNB/NCW'
dept_dict['nfb.gc.ca'] = 'NFB/ONF'
dept_dict['nrccan-rncan.gc.ca'] = 'NRCAN/RNCAN'
dept_dict['nserc-crsng.gc.ca'] = 'NSERC/CRSNG'
dept_dict['pbc-clcc.gc.ca'] = 'PBC/CLCC'
dept_dict['pco.bcp.gc.ca'] = 'PCO/BCP'
dept_dict['pipsc.ca'] = 'PIPSC/IPFPC'
dept_dict['ps.sp.gc.ca'] = 'PS/SP'
dept_dict['servicecanada.gc.ca.gc.ca'] = 'HRSDC/RHDSC'
dept_dict['fintrac-canafe.gc.ca'] = 'FINTRAC'

users = users.replace({'Department': dept_dict})

users['Time'] = pd.to_datetime(users['Time'], format = '%Y-%m-%d')
users['Month'] = users['Time'].map(lambda x: 1000*x.year + x.month)

#%%
#This gives the Users by Department By Month in GCconnex
crosstab = pd.crosstab(users.Department, users.Month).apply(lambda r: r.cumsum(), axis=1)
crosstab.to_csv(save_path+'December Monthly Users.csv')
#%%
#This gives the total amount of registrations by month
regpermonth = users.groupby('Month').count()
#%%
#Gives the amount of Users per month
regpermonth['Total'] = regpermonth['User'].cumsum()
usersbymonth = regpermonth[['Total']]
#%%
#I'm gonna try combining them into the same thing cause yolo
regpermonth['% Change'] = (regpermonth['User']/regpermonth['Total'])*100
regpermonth = regpermonth[['User', 'Total', '% Change']]
#%%

