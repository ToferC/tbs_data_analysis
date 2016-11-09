# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 08:14:45 2015

@author: Owner
"""

#Help Desk Stats Analysis
#3 Hypotheses to test:
#H1: Helpdesk use increases with more registered users - more significant if disproven
#H2: Helpdesk use increases with current activity increases
#H3: Helpdesk is used by certain types of people (the hard one)

#Importing Modules
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import seaborn as sns
#%%

#For this analysis, I'm going to need a lot of different datasets.
#The whole aim of the game here is to correlate the helpdesk statistics with all the
#other data that I have access to.

#NOTE: I added my own custom headers before porting them into Spyder
save_path = r'/Users/Owner/Documents/Work_transfer/Data/Helpdesk Analysis/Completed Product/'
data_path = r'/Users/Owner/Documents/Work_transfer/Data/Helpdesk Analysis/'
#%%
#Importing all the data in one cell (just for ease)
#Also Apparently Canada has its own custom encoding, so if it doesn't load,
#use the 'cp863' encoding
HDaug = pd.read_csv(data_path+'HD Aug.csv', encoding = 'cp863') #Helpdesk CSV August
HDsep = pd.read_csv(data_path+'HD Sep.csv', encoding = 'cp863') #Helpdesk CSV September
HDoct = pd.read_csv(data_path+'HD Oct.csv', encoding = 'cp863') #Helpdesk CSV October
HDnov = pd.read_csv(data_path+'HD Nov.csv') #Ditto November
google = pd.read_csv(data_path+'GA Aug1-Nov10.csv', parse_dates = [0]) #Google Analytics Views
Bcom = pd.read_csv(data_path+'Blog Comments.csv') #Blog Comments
Dcom = pd.read_csv(data_path+'Discussion Comments.csv') #Discussion Comments
Users = pd.read_csv(data_path+'November 17 Users.csv') #Users as of Nov 17
Groups = pd.read_csv(data_path+'Groups joined email.csv') #Groups Joined

#%%

#First thing is first, we need to join all the helpdesk dataframes into one long one with
#All the dates for time series analysis

#The first issue is that there is a slight difference in data collection
#between Aug-September and Oct-Nov, where one collects email, and the other email addresses
columns1 = ['Date', 'Name', 'Request', 'Department', 'Concluded Date']
aug = HDaug[columns1]
sep = HDsep[columns1]

columns2 = ['Date', 'Email address', 'Request', 'Department', 'Concluded Date']
octo = HDoct[columns2]
nov = HDnov[columns2]

#I didn't notice before, but there are a few summary stats columns at the bottom of the CSV's
#These lines get rid of them EZ-PZ
aug.dropna(inplace = True)
sep.dropna(inplace = True)
octo.dropna(inplace = True)
nov.dropna(inplace = True)

#Setting them altogether
colnames = ['Date', 'Name', 'Request', 'Department', 'End Date']
aug.columns = colnames
sep.columns = colnames
octo.columns = colnames
nov.columns = colnames

hdlist = [aug, sep, octo, nov]

#There's an issue with formatting of the dates that I've found, so this corrects it
#retroactively
for i in hdlist:
    i['Date'] = i['Date'].str.replace('--', '-')
    i['Date'] = i['Date'].str.replace('20115', '2015')
    i['Date'] = i['Date'].str.replace('2215', '2015')

      
        
#%%
for i in hdlist:
    i['Date'] = pd.to_datetime(i['Date'], format='%Y-%m-%d')  
    print (type(i['Date']))
    
#%%
helpdesk = pd.concat(hdlist)

if len(helpdesk) == len(aug) + len(octo) + len(nov) + len(sep):
    print ("concatenated well")
else:
    raise ValueError("You didn't concatenate how you wanted")
    
#We're good then
    
helpdesk = helpdesk.sort('Date')
#Some of the dates are weirdly formatted, so in the interest of time, I am just going
#To cut those things out
startdate = np.datetime64('2015-08-01')
enddate = np.datetime64('2015-11-15')

helpdesk = helpdesk[(helpdesk['Date'] >= startdate) & (helpdesk['Date'] <= enddate)]
#We now have a helpdesk dataset that we can play with if we so choose....Which we do
#%%
#Google Analytics is already pretty well formatted
google = google[:-1] #Just fixing the last row because it's strange
#%%
#Combining helpdesk requests amounts per day to Google Analytics stats
hdrequests = helpdesk.groupby('Date').count()
hdrequests = hdrequests['Name']
hdrequests = hdrequests.reset_index()
google.columns = ['Date', 'Users', 'Sessions']
covdf = pd.merge(hdrequests, google, on='Date')

covariance = covdf.cov() 
correlation = covdf.corr() #Covariance and Correlation show that sessions and users are
#very very similar

covdf.describe()
#A rather not surprising result is that as there continues to be activity on the platform
#The amount of requestions starts to increase.
#%%
#Users and Sessions are very similar, but I'm going to use Users for the purpose
#of better interpretation
x = covdf['Users']
y = covdf['Name']
corrcoef = stats.pearsonr(x,y) #This calcuates the correlation coefficient between
#The amount of helpdesk complaints in a day, and the amount of users on GCconnex in a day
#The P-value suggests that it is statistically significant at the 99% level.

#But still a weak correlation
#%%
#Before I forget, I think it would be really cool if we could use users, correlate it
#with amount of helpdesk requests, and if there is a constant-ness to it, then we can
#use that to make projections of the helpdesk requests

Users['TimeCreated'] = Users['TimeCreated'].astype('datetime64[s]')
Users['TimeCreated'] = pd.to_datetime(Users['TimeCreated'], format = '%Y-%m-%d')
#%%
users = Users.set_index('TimeCreated')
usersreg = users.resample('D', how='count')
usersreg = usersreg.reset_index()
usersreg = usersreg[(usersreg['TimeCreated'] >= startdate) & (usersreg['TimeCreated'] <= enddate)]
usersreg.columns = ['Date', 'Registrations', 'dontmatter']
usersreg.drop('dontmatter', inplace=True, axis=1)
#usersreg is the number of registrations in a given day
#%%
#Merging registrations and helpdesk requests
registrationdf = pd.merge(usersreg, hdrequests, on='Date')
#Let's do another correlation on the new registrations and helpdesk requests in a day

x = registrationdf['Registrations']
y = registrationdf['Name']

regcorrcoef = stats.pearsonr(x,y) #Weak

#More significant than the other, but the same impact probably

#%%
#This part is going to check how helpdesk requests have changed as a function of population

pop = users.resample('D', how = 'count')
pop['Population'] = pop['Name'].cumsum()

pop.reset_index(inplace = True)

pop = pop[(pop['TimeCreated'] >= startdate) & (pop['TimeCreated'] <= enddate)]

#To merge properly, need to change the date name
pop.columns = ['Date', 'Users', 'users', 'Population']
popdf = pop[['Date', 'Population']]

registrationdf = pd.merge(registrationdf, popdf, on='Date')

x = registrationdf['Population']
#Don't have to rename y because its the same

populationcorrcoef = stats.pearsonr(x,y)
#Super significant, but also not that high

#%%
#Now let's see if we can liken some statistics to other people
#This is just to see if I can standardize how names are
helpdesk['Name'] = helpdesk['Name'].str.replace('mailto:', '')
helpdesk['Name'] = helpdesk['Name'].str.lower()
helpdesk[['Name', 'Column']] = helpdesk['Name'].apply(lambda x: pd.Series(x.split('@')))
helpdesk.drop('Column', axis=1, inplace = True)
#%%
#Looking into the data, there are several parts with typos
#Gotta clean them up
helpdesk['Request'] = helpdesk['Request'].str.replace('delete account', 'delete')
helpdesk['Request'] = helpdesk['Request'].str.replace('groups', 'group')
helpdesk['Request'] = helpdesk['Request'].str.replace('registration ', 'registration')
helpdesk['Request'] = helpdesk['Request'].str.replace('techinical', 'technical')
helpdesk['Request'] = helpdesk['Request'].str.replace('technical ', 'technical')
helpdesk['Request'] = helpdesk['Request'].str.replace('tecnica', 'technical')
helpdesk['Request'] = helpdesk['Request'].str.replace('password issue', 'password')
helpdesk['Request'] = helpdesk['Request'].str.replace('groups', 'group')
helpdesk['Request'] = helpdesk['Request'].str.lower()
#%%
#citest is making a cross-tab on how often people make help desk requests and at 
#what dates they are actually making the requests
clientinfo = helpdesk.groupby(['Name', 'Date']).count()
citest = pd.crosstab(helpdesk.Name, helpdesk.Date)
citest['Total'] = citest.sum(axis=1)

if citest['Total'].sum() != len(helpdesk): #A statement to stop me from making mistakes
    raise ValueError('This is not right')
#%%
#Now there is work to be done to integrate platform activity with helpdesk stats
#In the interest of time (and past precedent), I'm going to look at user activity
#based on comments (on both discussions and blogs) and groups joined
#Just have to clean them up
userlist = [Bcom, Dcom, Groups]
for i in userlist:    
    i[['Name', 'Department']] = i['Email'].apply(lambda x: pd.Series(x.split('@')))
    i.drop('Department', 1, inplace=True)
    i['Name'] = i['Name'].str.lower()


blog = Bcom.groupby('Name').count()
discussion = Dcom.groupby('Name').count()
groups = Groups.groupby('Name').count()

newlist = [blog, discussion, groups]

for i in newlist:
    i = i.reset_index(inplace = True)
#%%
names = ['Name', 'GUID']
blog = blog[names]
discussion = discussion[names]
groups = groups[names]

blog.columns = ['Name', 'Blog Comments']
discussion.columns = ['Name', 'Discussion Comments']
groups.columns = ['Name', 'Groups Joined']

#%%
#This is initially slightly problematic because it only includes people who have commented
#on a blog, joined a group AND commented on a discussion, very small sample size
#I am trash garbage
useractivity = pd.merge(blog, discussion, on = 'Name', how='outer')
useractivity = pd.merge(useractivity, groups, on = 'Name', how='outer')


cimerge = citest.reset_index()
cimerge = cimerge[['Name', 'Total']]
cimerge.columns = ['Name', 'Help Desk Requests']
useractivity = pd.merge(useractivity, cimerge, on = 'Name', how = 'outer')
useractivity = useractivity.fillna(0)
useractivity['Comments'] = useractivity['Blog Comments'] + useractivity['Discussion Comments'] 
#This has WAY too many observations, but is a good start
#%%

hdactivity = useractivity[(useractivity['Help Desk Requests'] >= 1)]

#%%
#Now to run a regression on helpdesk requests and activity

hdr = hdactivity['Help Desk Requests']
com = hdactivity['Comments']
gj = hdactivity['Groups Joined']

model = smf.ols(formula='hdr ~ com + gj', data = hdactivity)
res = model.fit()
print (res.summary())
#There is no real significant impacts. The impact wo
#%%
#Using a larger sample size that includes zeros
#Again, nothing much to say here
hdru = useractivity['Help Desk Requests']
comu = useractivity['Comments']
gju = useractivity['Groups Joined']

model1 = smf.ols(formula = 'hdru ~ + comu + gju', data = useractivity)
res1 = model1.fit()
print (res1.summary())

#%%

useractivity['Made Request'] = useractivity['Help Desk Requests']
def f(x):
    if x > 0:
        return 1
    else:
        return 0

useractivity['Made Request'] = useractivity['Made Request'].apply(f)
ua = useractivity['Made Request']
formula = 'ua ~ + comu + gju'
mlm = smf.glm(formula = formula, family = sm.families.Binomial(), data = useractivity).fit()
mlm.summary()
#%%

#Plotting Helpdesk Requests over a three month span
hdrequests['Cumulative'] = hdrequests['Name'].cumsum()
x = hdrequests['Date']
y = hdrequests['Cumulative']

plot = plt.plot(x,y)
plt.show()


#%%
#Plotting the frequency of Helpdesk days
#I wish I had more data for this to be honest
freqdata = hdrequests.groupby('Name').count()

plt.plot(freqdata['Date'])
plt.xlabel('Number of Requests')
plt.ylabel('Frequency')
plt.title('Help Desk Frequency')
plt.axis([0,25,0,8])
plt.show()

#%%
regplot = plt.plot(hdrequests['Date'], hdrequests['Name'], label = 'Help Desk Requests')
totalplot = plt.plot(hdrequests['Date'], hdrequests['Cumulative'], label = 'Cumulative Total')
plt.xlabel('Date')
plt.ylabel('Requests')
plt.title('Help Desk Activity - August 1, 2015 to Nov 10, 2015')
plt.legend()
plt.savefig(save_path+'Help Desk Cumulative and Daily.png')
plt.show()
#%%
#Couple more things to do now
categories = helpdesk.groupby('Request').count()

augcat = aug.groupby('Request').count()
sepcat = sep.groupby('Request').count()
octcat = octo.groupby('Request').count()
novcat = nov.groupby('Request').count()

catlist = [augcat, sepcat, octcat, novcat]
for i in catlist:
    i.reset_index(inplace = True)

augcat = augcat[['Request', 'Name']]
sepcat = sepcat[['Request', 'Name']]
octcat = octcat[['Request', 'Name']]
novcat = novcat[['Request', 'Name']]
    
augcat.columns = [['Request', 'August']]
sepcat.columns = [['Request', ' September']]
octcat.columns = [['Request', 'October']]
novcat.columns = [['Request', 'November (Half)']]
#%%

categories = pd.merge(augcat, sepcat, on = 'Request', how = 'outer')
categories = pd.merge(categories, octcat, on = 'Request', how = 'outer')
categories = pd.merge(categories, novcat, on = 'Request', how = 'outer')
categories.fillna(0, inplace = True)
categories['Total'] = categories.sum(axis = 1)
categories.to_csv(save_path+'Categories of Request per Month.csv')
#%%

#The final thing that I want to do with this check the issue resolved date and combine it
#with last active date to see how people react at the help desk
#This is sort of ad-hoc though, so I'm gonna import the dataset here.
activity = pd.read_csv(data_path + 'Actions for Users.csv')
activity[['Name', 'Department']] = activity['Email'].apply(lambda x: pd.Series(x.split('@')))
activity.drop('Useless', 1, inplace = True)
activity['Name'] = activity['Name'].str.lower()
activity = activity[['Name', 'Last Action', 'Time Created']]
activityrequest = pd.merge(activity, helpdesk, how='inner', on='Name')
#%%
#This cell is just cleaning up really
activityrequest['Last Action'] = pd.to_datetime(activityrequest['Last Action'])
activityrequest['Time Created'] = pd.to_datetime(activityrequest['Time Created'])
#Typos need to be fixed
activityrequest['End Date'] = activityrequest['End Date'].str.replace('22015', '2015')
activityrequest['End Date'] = activityrequest['End Date'].str.replace('20154', '2015')
activityrequest['End Date'] = activityrequest['End Date'].str.replace('21015', '2015')
activityrequest['End Date'] = activityrequest['End Date'].str.replace('20115', '2015')
activityrequest['End Date'] = activityrequest['End Date'].str.replace('--', '-')
activityrequest['End Date'] = pd.to_datetime(activityrequest['End Date'])

#This is going to measure the time it took for requests to be completed according to the
#dataset
#%%
#Calculating time deltas to determine time lags in activity.
#This calculates the differences in measurement 
activityrequest['Response Time'] = activityrequest['End Date'] - activityrequest['Date']
activityrequest['Request Lag'] = activityrequest['Date'] - activityrequest['Time Created']
activityrequest['Action After Request'] = activityrequest['Last Action'] - activityrequest['End Date']
#%%

timefilter = pd.Timedelta(days=500)
dawnoftime = pd.to_datetime('1969-12-31')
activityrequest = activityrequest[activityrequest['Last Action'] != dawnoftime]
activityrequest = activityrequest[activityrequest['Response Time'] >= 0]
#%%
#This is a measurement of the response time for helpdesk requests
responsetimecounts = activityrequest['Response Time'].value_counts()
responsetimecounts = responsetimecounts.sort_index()

#%%
#This is under the assumption that people who have an activity recorded
#AFTER they've received help desk help are continuing on their way
#Those who have not recorded activity after a helpdesk response may have been unsatisfied
actionafterrequest = activityrequest[activityrequest['Action After Request'] > 0]
actionbeforerequest = activityrequest[activityrequest['Action After Request'] < 0]
print ("How many people have a last action AFTER they made a help desk request")
print (len(actionafterrequest))
print ("How many people have a last action BEFORE they made a help desk request")
print (len(actionbeforerequest))
print ("Have made an action on same day")
print (len(activityrequest[activityrequest['Action After Request'] == 0]))
#%%
aarct = pd.crosstab(actionafterrequest['Action After Request'], actionafterrequest['Request'])
abrct = pd.crosstab(actionbeforerequest['Action After Request'], actionbeforerequest['Request'])

#These are to calculate average time metrics
aar = actionafterrequest[['Request', 'Response Time', 'Request Lag', 'Action After Request']]
aar1 = aar.groupby('Request').sum()
aar2 = aar.groupby('Request').count()
aar1.reset_index(inplace = True)
aar2.reset_index(inplace = True)

aar1.columns = ['Request', 'Total Response Time', 'Total Request Lag', 'Total Action After Request']
aar2 = aar2[['Request', 'Response Time']]
aar2.columns = ['Request', 'Number of Requests']
aar = pd.merge(aar1, aar2, on = 'Request')

aar['Average Response Time'] = aar['Total Response Time']/aar['Number of Requests']
aar['Average Request Lag'] = aar['Total Request Lag']/aar['Number of Requests']
aar['Average Action Time After Request'] = aar['Total Action After Request']/aar['Number of Requests']



#%%
#To calculate average time metrics
abr = actionbeforerequest[['Request', 'Response Time', 'Request Lag', 'Action After Request']]
abr1 = abr.groupby('Request').sum()
abr2 = abr.groupby('Request').count()

abr1.reset_index(inplace = True)
abr2.reset_index(inplace = True)
abr1.columns = ['Request', 'Total Response Time', 'Total Request Lag', 'Total Action After Request']
abr2 = abr2[['Request', 'Response Time']]
abr2.columns = ['Request', 'Number of Requests']



abr = pd.merge(abr1, abr2, on = 'Request')
abr['Average Response Time'] = abr['Total Response Time']/abr['Number of Requests']
abr['Average Request Lag'] = abr['Total Request Lag']/abr['Number of Requests']
abr['Average Action Time After Request'] = abr['Total Action After Request']/abr['Number of Requests']

#%%
aar.to_csv(save_path+'Time Metrics for Actions AFTER Resolution.csv')
abr.to_csv(save_path+'Time Metrics for Actions BEFORE Resolution.csv')
#%%
atr = activityrequest[['Request', 'Response Time', 'Request Lag', 'Action After Request']]
atr1 = atr.groupby('Request').sum()
atr2 = atr.groupby('Request').count()

atr1.reset_index(inplace = True)
atr2.reset_index(inplace = True)
atr1.columns = ['Request', 'Total Response Time', 'Total Request Lag', 'Total Action After Request']
atr2 = atr2[['Request', 'Response Time']]
atr2.columns = ['Request', 'Number of Requests']

atr = pd.merge(atr1, atr2, on = 'Request')
atr['Average Response Time'] = atr['Total Response Time']/atr['Number of Requests']
atr['Average Request Lag'] = atr['Total Request Lag']/atr['Number of Requests']
atr['Average Action Time After Request'] = atr['Total Action After Request']/atr['Number of Requests']

atr.to_csv(save_path+'Time Metrics All.csv')
#%%
#Plotting a link between Users on GCconnex on a given day and helpdesk requests
ax = plt.gca()
ax2 = ax.twinx()
dates = covdf['Date']
gusers = ax.plot(dates, covdf['Users'], label='Users')
hdreq = ax2.plot(dates, covdf['Name'], color = 'g', label = 'Help Desk Requests')
ax.set_ylabel("Online Users")
ax2.set_ylabel("Help Desk Requests")
ax.set_xlabel('Date')
plt.title("Active Users vs. Help Desk Requests")
ax2.grid(False)
ax.legend()
plt.legend(loc = 'upper left')
plt.show()

#%%

