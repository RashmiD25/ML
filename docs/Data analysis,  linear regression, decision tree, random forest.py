

import numpy as np
import pandas as pd
def mape(y, yhat):
    return np.mean(np.absolute((y - yhat) / y))


# """Let's carry out data analytics of the hourly price & load data of the PJM market in 2021.

# Import the 3 data sets `da_hrl_lmps.csv`, `rt_hrl_lmps.csv`, and `hrl_load_metered.csv`, merge them into a single `pandas.DataFrame`, with the following variables: `datetime_beginning_ept` (beginning time of the hour, Eastern Prevailing Time), `total_lmp_da` (day-ahead price), `total_lmp_rt` (real-time price), and `mw` (load). 

# Contemplate: why do we get more than 24 rows for November 7, 2021?
# """

ds1 = pd.read_csv('da_hrl_lmps.csv')
ds2 = pd.read_csv('rt_hrl_lmps.csv')
ds3 = pd.read_csv('hrl_load_metered.csv')

ds1 = ds1.drop(['datetime_beginning_utc', 'pnode_id', 'pnode_name', 'voltage', 'equipment', 'type', 'zone', 'system_energy_price_da',
                'congestion_price_da', 'marginal_loss_price_da', 'row_is_current', 'version_nbr'], axis=1)
ds1['datetime_beginning_ept'] = pd.to_datetime(ds1['datetime_beginning_ept'])
ds2 = ds2.drop(['datetime_beginning_ept', 'datetime_beginning_utc', 'pnode_id', 'pnode_name', 'voltage', 'equipment', 'type', 'zone', 
                'system_energy_price_rt', 'congestion_price_rt', 'marginal_loss_price_rt', 'row_is_current', 'version_nbr'], axis=1)

ds3 = ds3.drop(['datetime_beginning_ept', 'datetime_beginning_utc', 'nerc_region', 'zone', 'mkt_region', 'load_area', 'is_verified'],axis=1)

df123=pd.concat([ds1,ds2,ds3],axis=1)
df123

df123['Dates'] = pd.to_datetime(df123['datetime_beginning_ept']).dt.date
df123['Dates'] = pd.to_datetime(df123['Dates'], format='%Y-%m-%d')

print(df123[df123['Dates'] == '2021-11-7'])
print(len(df123[df123['Dates'] == '2021-11-7']))

# Extra hour due to the daylight saving time.
# Answer:
# The specified date is during winter months where there's a difference of 1 extra hour behind UTC which we can see from the dataframe as 1 AM, having
# two values. Hence, the 1 extra row

# """Finding row with the highest day-ahead price, the row with the lowest day-ahead price, the row with the highest real-time price, the row with the lowest real-time price, the row with the highest load, and the row with the lowest load."""

print('Row with the highest day-ahead price:')
print(df123[df123['total_lmp_da'] == df123['total_lmp_da'].max()])

print('Row with the lowest day-ahead price:')
print(df123[df123['total_lmp_da'] == df123['total_lmp_da'].min()])

print('Row with the highest real-time price:')
print(df123[df123['total_lmp_rt'] == df123['total_lmp_rt'].max()])

print('Row with the highest real-time price:')
print(df123[df123['total_lmp_rt'] == df123['total_lmp_rt'].min()])

print('Row with the highest load:')
print(df123[df123['mw'] == df123['mw'].max()])

print('Row with the highest load:')
print(df123[df123['mw'] == df123['mw'].min()])

hour1data=[]
for x in df123['total_lmp_da'][df123['datetime_beginning_ept'].astype(str).str.contains('01:00:00')]: 
    hour1data.append(x)

len(hour1data)

# why more than other hours' data ???

# """Next, for each of the 24 hours (defining `00:00:00` as hour 0, `01:00:00` as hour 1, etc.), calculate the mean and the standard deviation of the day-ahead price, and the mean and the standard deviation of the real-time price."""

print('For day-ahead price=>')
import statistics 
hours=['00:00:00','01:00:00','02:00:00','03:00:00','04:00:00','05:00:00','06:00:00','07:00:00','08:00:00','09:00:00','10:00:00','11:00:00','12:00:00','13:00:00','14:00:00','15:00:00','16:00:00','17:00:00','18:00:00','19:00:00','20:00:00','21:00:00','22:00:00','23:00:00']

for i in hours:
  hourdata=[]
  for x in df123['total_lmp_da'][df123['datetime_beginning_ept'].astype(str).str.contains(i)]: 
    hourdata.append(x)
  hourmean=statistics.mean(hourdata)
  hourvar=statistics.stdev(hourdata)
  # print('hour '+i.split(':')[0]+' data: '+str(hourdata))
  print('Mean & Variance of hour '+i.split(':')[0]+': '+str(hourmean), str(hourvar))

print('For the real-time price=>')
for i in hours:
  hourdataRt=[]
  for x in df123['total_lmp_rt'][df123['datetime_beginning_ept'].astype(str).str.contains(i)]: 
    hourdataRt.append(x)
  hourmeanRt=statistics.mean(hourdataRt)
  hourvarRt=statistics.stdev(hourdataRt)
  # print('hour '+i.split(':')[0]+' data: '+str(hourdataRt))
  print('Mean & Variance of hour '+i.split(':')[0]+': '+str(hourmeanRt), str(hourvarRt))

# """Defining spread = day-ahead price - real-time price. For which of the 24 hours do we reject the null hypothesis that the mean of the spread is equal to zero, at a significance level of 5\%? """

from scipy import stats

def spread(hourX) :
    return (df123['total_lmp_da'].loc[df123['datetime_beginning_ept'].astype(str).str.contains(hourX)] -  df123['total_lmp_rt'].loc[df123['datetime_beginning_ept'].astype(str).str.contains(hourX)])

for i in hours:
  out=0
  out=stats.ttest_1samp(spread(i),0)
  print('hour '+i.split(':')[0]+'='+str(out))
  if out.pvalue>=0.05:
    print('Do not reject H0')
  else:
    print('Reject H0')

# therefore, we reject the null hypothesis for the Hours: 7, 8, 9, 14, 20, 21, 22, 23

# """For each of the 12 months, let's fit a simple linear regression model of the day-ahead price (target) on the load (feature), and another simple linear regression model of the real-time price (target) on the load (feature) i.e; reporting the $R^2$ of each model, for each month (such that there are 24 values in total)."""

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# simple linear regression model of the day-ahead price on the load 
print("day-ahead price vs load ")
for idx,month_i in enumerate(months):
  monthData = df123[df123['datetime_beginning_ept'].dt.month == idx+1]
  train1, test1= train_test_split(monthData, test_size=0.3)
  X_train1 = train1[['mw']]
  y_train1 = train1[['total_lmp_da']]
  model1 = LinearRegression().fit(X_train1, y_train1)
  r_squared = model1.score(X_train1, y_train1)
  print('R^2 for '+str(month_i)+' = '+str(r_squared))

# simple linear regression model of the real-time price on the load 
print("real-time price vs load ")
for idx,month_i in enumerate(months):
  monthData = df123[df123['datetime_beginning_ept'].dt.month == idx+1]
  train2, test2= train_test_split(monthData, test_size=0.3)
  X_train2 = train2[['mw']]
  y_train2 = train2[['total_lmp_rt']]
  model1 = LinearRegression().fit(X_train2, y_train2)
  r_squared = model1.score(X_train2, y_train2)
  print('R^2 for '+str(month_i)+' = '+str(r_squared))

# """Next, fit a decision tree model to solve a classification problem. Data file = `data/p2/fridge.txt`. In each line, there are three numbers: the first number is the power consumption (in Watts), the second number is the duration (in seconds), and the third number is the label (1 for refrigerator 1, and -1 for refrigerator 2). The task is to fit a tree model in which power and duration are the predictors, and label is the response (that is, given a pair of power and duration, is it refrigerator 1 or refrigerator 2?).

# First, we need to import the data, which is a little tricky since the data file is not properly formatted. Then randomly sample 300 observations as the test set, and the remaining observations constitute the training set. There is no validation set in this problem. Then using `sklearn.tree.DecisionTreeClassifier` we fit a tree model to the training set. Finally, we'll calculate the accuracy of the generated tree model on the test set.

# """

import random
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
seperator = '  '
fridgeMatrix = []

with open('fridge.txt', 'r') as f:
    for line in f:
        # generating an array with the elements which are in a single line
        line_array = line.split(seperator)
        fridgeMatrix.append(line_array)

# randomly sampling 300 observations as the test set, and the remaining observations as the training set.
random.shuffle(fridgeMatrix)
# dropping 1st column with only space and getting rid of \n is last columns
fridgeMatrix = pd.DataFrame(fridgeMatrix)
fridgeMatrix = fridgeMatrix.drop([0],axis=1)
for index, row in fridgeMatrix.iterrows():
  row[3]= row[3].strip('\n')

test_data = fridgeMatrix[:300]
train_data = fridgeMatrix[300:]
# power and duration are the predictors(features), and label is the response(target)
X_train = train_data[[1,2]]
y_train = train_data[[3]]
X_test = test_data[[1,2]]
y_test = test_data[[3]]

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()
clf = clf.fit(X_train,y_train)
y_pred = clf.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

# """## 

# The data file `df_nan.csv` contains 5-year load and temperature data of an area in EST. The load (`kw`) is in kW, and the temperature (`tmpf`) is in degree Fahrenheit.

# The load data of 28 selected days (2021-04-04, 2021-04-14, ..., 2021-12-30, with 10 days apart), as well as the data of the previous and the following days of each of the selected days, are removed to mimic day-ahead forecasting. Hence, we'll develop a forecasting model and forecast the hourly load of each of the selected days.

# For eg, the first selected day is 2021-04-04; then we need to forecast the hourly load of 2021-04-04.

# The model that can be used in this case is time series forecasting model.
# """

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
dfNan = pd.read_csv('df_nan.csv')
dfNan

dfNan['year'] = pd.to_datetime(dfNan['ept']).dt.year
dfNan['month'] = pd.to_datetime(dfNan['ept']).dt.month
dfNan['day'] = pd.to_datetime(dfNan['ept']).dt.day
dfNan['hour'] = pd.to_datetime(dfNan['ept']).dt.hour
dataNan = dfNan.drop(['utc', 'ept'], axis=1)
dataNan

# Dropping the null values from the dataset to create a train data for model
# nan_values = data[data['kw'].isna()]

dataNan.dropna(inplace=True)

dataNan.info()

## splitting dataframes into features and target
X = dataNan.drop(['kw'], axis = 1)
y = dataNan['kw']
X_train = X
y_train = y
print('training set size: {}'.format(X_train.shape))

# CREATING A TEST DATA SET
test_data = pd.read_csv('template.csv')
test_data1 = test_data.copy()
test_data

### converting utc to datetime type using python package datetime
test_data['year'] = pd.to_datetime(test_data['ept']).dt.year
test_data['month'] = pd.to_datetime(test_data['ept']).dt.month
test_data['day'] = pd.to_datetime(test_data['ept']).dt.day
test_data['hour'] = pd.to_datetime(test_data['ept']).dt.hour

dropped_data = test_data.drop(['utc', 'ept'], axis=1)
dropped_data

Xt = dropped_data.drop(['kw'], axis = 1)
X_test = Xt
X_test
print('test set size: {}'.format(X_test.shape))

# Training RandomForestRegressor
model = RandomForestRegressor(random_state = 42).fit(X_train, y_train)
pred_y = model.predict(X_test)

pred_y

print(test_data1.shape)
print(pred_y.shape)
test_data1['kw'] = pred_y
test_data1
test_data1.to_csv('outputs.csv', header=False, index=False)
