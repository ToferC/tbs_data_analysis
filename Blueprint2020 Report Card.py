# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 14:26:38 2015

@author: Owner
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 15:35:28 2015

@author: Owner
"""

import pandas as pd
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import os

#%%

data_path = r'/Users/Owner/Documents/Work_transfer/Data/Report Card/'
key_path = r'/Users/Owner/Documents/Work_transfer/Data/GCconnex/Profile Statistics/'
bp_path = r"C:/Users/Owner/Documents/Work_transfer/Data/GCconnex/"

#%%

avout = pd.read_csv(data_path+'AvatarAboutme.csv', header=None)
colleagues = pd.read_csv(data_path+'Colleagues.csv', header=None)
groups = pd.read_csv(data_path+'Groups.csv', header=None)
users = pd.read_csv(data_path+'RealUsers.csv',  header=None)
skills = pd.read_csv(data_path+'Skills.csv', header=None)
members = []
#%%
#Importing a dataset that contains solely BP2020 group members

with open(os.path.join(bp_path+'BP2020 Users.csv'), "r") as f:
    reader = csv.reader(f, delimiter = ',')
    next(reader)

    for row in reader:
        guid = int(row[1])
        members.append(guid)
        



#%%

#Working with the About me and Avatar Set
#I was a moron and never actually gave the columns names so I'm gonna do that for the
#Relevant columns

columns = ['Code', 'ID', 'User GUID', 'Time Created', 'Date2']
avout.columns= columns

aboutme = avout.loc[avout['Code'] == 55]
avatar = avout.loc[avout['Code'] == 73]

aboutme.drop_duplicates(inplace=True)
avatar.drop_duplicates(inplace=True)

#Let's just drop a bunch of columns that we don't need

aboutme = aboutme[['Code', 'User GUID']]
avatar = avatar[['Code', 'User GUID']]
aboutme['About_me'] = aboutme['Code']
aboutme.drop('Code', 1, inplace=True)
avatar['Avatar'] = avatar['Code']
avatar.drop('Code', 1, inplace=True)

#%%

if (aboutme['About_me'] == 55).sum() == len(aboutme):
    print ("We gucci baby!!")
else:
    print ("Check your work")

if (avatar['Avatar'] == 73).sum() == len(avatar):
    print ("We got our swagger up!!!")
else:
    print ("Swag not on lock...")

#%%

mainframe = pd.merge(aboutme, avatar, how='outer', on='User GUID')

#%%
#Working on the colleagues dataset now
colcols = ['User GUID', 'Relationship', 'Friend GUID', 'Time']
colleagues.columns = colcols

colleagues.drop('Time', 1, inplace=True)
colleagues.drop('Relationship', 1, inplace=True)

#The way that the colleagues dataset is set up is that it monitors the colleagues sender
#and the colleague receiver of requests. If a colleague request is accepted, it is double counted


colleaguecount = colleagues.groupby('User GUID').count()
colleaguecounttest = colleagues.groupby('Friend GUID').count()

colleaguecount.reset_index(drop=False, inplace=True)
colleaguecount.columns = ['User GUID', 'Colleague_count']
colleaguecounttest.reset_index(drop=False, inplace=True)
colleaguecounttest.columns = ['User GUID', 'Colleague_count']

mainframe = pd.merge(mainframe, colleaguecount, how='outer', on='User GUID')

mainframe.drop_duplicates(inplace=True)

mainframe = mainframe.fillna(0)

#%%
#Adding users and using the emails for departments

usercol = ['User GUID', 'Email', 'Name', 'UnixTime']
users.columns = usercol

users[['User', 'Department']] = users['Email'].str.split('@', expand=True)

users = users[['User GUID', 'User', 'Department']]
users['Department'] = users['Department'].str.lower()

#%%

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

#%%

mainframe = pd.merge(mainframe, users, how='outer', on='User GUID')

#%%
#Last dataset to put in is group membership

groupcol = ['User GUID', 'Relationship', 'Group ID', 'Time']
groups.columns = groupcol

if (groups['Relationship'] == 'member').sum() == len(groups):
    print ("The relationship column only says member")
else:
    print ("You done goofed son")

groupsgroup = groups.groupby('User GUID').count()
groupsgroup.reset_index(drop=False, inplace=True)

groupsgroup = groupsgroup[['User GUID', 'Group ID']]
groupsgroup.columns = ['User GUID', 'Groups Joined']

mainframe = pd.merge(mainframe, groupsgroup, how='outer', on='User GUID')

#%%
skillscol = ['User GUID', 'Number?', 'Skill']
skills.columns = skillscol

skillscount = skills.groupby('User GUID').count()
skillscount.drop('Number?', 1, inplace=True)
skillscount.reset_index(drop=False, inplace=True)

mainframe = pd.merge(mainframe, skillscount, how='outer', on='User GUID')


#%%

mainframe = mainframe.fillna(0)

def g(x):
    if x == 55:
        return 1
    else:
        return 0
    
def h(x):
    if x == 73:
        return 1
    else:
        return 0
        
mainframe['About_me'] = mainframe['About_me'].apply(g)
mainframe['Avatar'] = mainframe['Avatar'].apply(h)
mainframe = mainframe[['User', 'User GUID', 'Department', 'About_me', 'Avatar', 'Colleague_count', 'Groups Joined', 'Skill']]
#%%
#Adding a discrete variable to indicate whether people meet a certain threshold of groups and colleagues
#In this case, the threshold is >= 5

colleague_thresh = mainframe

def i(x):
    if x >= 5:
        return 1
    else:
        return 0
def f(x):
    if x >= 1:
        return 1
    else:
        return 0
mainframe['Colleague_thresh'] = colleague_thresh['Colleague_count'].apply(i)
mainframe['Group_thresh'] = mainframe['Groups Joined'].apply(i)
mainframe['Skill'] = mainframe['Skill'].apply(f)
#%%
idb = pd.read_excel(data_path+'comments.xlsx')
idb = idb[['owner_guid', 'string']]
idb = idb.dropna()
comments = idb.groupby('owner_guid').count()
comments.reset_index(inplace=True)
comments.columns = ['User GUID', 'Comments']
comments = comments.convert_objects(convert_numeric = True).dropna()
mainframe = pd.merge(mainframe, comments, how='outer', on='User GUID')
mainframe = mainframe.fillna(0)

#%%
def i(x):
    if x >= 5:
        return 1
    else:
        return 0
mainframe['Comment_thresh'] = mainframe['Comments'].apply(i)
#%%
#Now to group the people by department
#Since I used 0's and 1's, I can do all of the metrics by sum
#Woop

departmentstats = mainframe[['Department', 'About_me', 'Avatar', 'Colleague_thresh', 'Group_thresh', 'Skill']]
departmentstats = departmentstats.groupby('Department').sum()

depstats = mainframe.groupby('Department').sum()


#%%
#Testing depstats and departmentstats to see if there is actual sense going on
testlist = [mainframe.About_me.sum(), mainframe.Avatar.sum(), mainframe.Colleague_thresh.sum(), mainframe.Group_thresh.sum(), mainframe.Skill.sum(), mainframe.Comment_thresh.sum()]
testlist2 = [(mainframe['About_me'] == 1).sum(), (mainframe['Avatar'] == 1).sum(), (mainframe['Colleague_thresh'] == 1).sum(), (mainframe['Group_thresh'] == 1).sum(), (mainframe['Skill'] == 1).sum(), (mainframe['Comment_thresh'] == 1).sum()]
print (testlist)
print (testlist2)

if testlist == testlist2:
    print ("Wow. You did it. Congratulations. You are smart. So smart. A genius if you will.")
else:
    print ("Try again moron")

#%%
depcounttime = users.groupby('Department').count()


#%% This script will go through and look and do all the heavy lifting, I just have
#to make sure that it will only deal with Blueprint2020 members

bpmembers = mainframe[mainframe['User GUID'].isin(members)]
bpmembers.to_csv(data_path+'BP2020 Profile Statistics Only.csv')