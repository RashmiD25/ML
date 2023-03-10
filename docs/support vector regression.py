# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn import svm
from sklearn.pipeline import make_pipeline
from sklearn.compose import TransformedTargetRegressor
def mape(a, f):
    return np.mean(np.absolute((a - f) / a))
df = pd.read_csv('bse_clean.csv', parse_dates=['Date'])
df['Day'] = df['Date'].dt.dayofweek
train = ((df['Date'].dt.year >= 2004) & (df['Date'].dt.year <= 2006))
test = ((df['Date'].dt.year >= 2007) & (df['Date'].dt.year <= 2008))
X = np.concatenate((OneHotEncoder(sparse=False).fit_transform(df[['Hour', 'Month', 'Day']]), df[['T']]), axis=1)
y = df['Load'].to_numpy()
model = TransformedTargetRegressor(make_pipeline(StandardScaler(), svm.SVR()), transformer=StandardScaler())
model.fit(X[train], y[train])
mape(y[test], model.predict(X[test]))

output-> 0.03004253188316352
# """To achieve a better accuracy, we will tune the parameters in `svm.SVR()`. The objective is simply to beat the performance of the default setting i.e; the following MAPE should be smaller than the above MAPE."""

# The value of 𝜖 defines a margin of tolerance where no penalty is given to errors.
# The support vectors are the instances across the margin, i.e. the samples being penalized, which slack variables are non-zero.
# The larger 𝜖 is, the larger errors we admit in our solution. By contrast, if 𝜖→0+, every error is penalized: we end with many (tending to the total number of instances) support vectors to sustain that.

model = TransformedTargetRegressor(make_pipeline(StandardScaler(), svm.SVR(epsilon = 0.01)), transformer=StandardScaler())
model.fit(X[train], y[train])
mape(y[test], model.predict(X[test]))


output-> 0.029768524572012515
# We observe that the mape obtained here is smaller than the previous one, without using epsilon. Hence, a better accuracy is acheived.

# """Now, adopting $k$-means clustering for daily load profiles:"""

from sklearn.cluster import KMeans
df = pd.read_csv('bse_clean.csv', parse_dates=['Date'])
df = df[df['Month'] == 10].copy()
df_wide = df.pivot('Date', 'Hour', 'Load').to_numpy()
kmeans = KMeans(2, random_state=0)
kmeans.fit(df_wide)
print(kmeans.labels_)

# """In above results, `1` = predicting weekday and `0` = predicting weekend. Using calendar information to calculate the accuracy of the prediction:"""

# we loop through df['Date'] for every unique day(not every hour) to find the original weekday/weekend
correct_labels=[]
index = 0
for i in range(len(df['Date']))[::24]:
  if (list(df['Date'])[i].weekday() <= 4):
    correct_labels.append(1)
  else:
    correct_labels.append(0)

print(correct_labels)

# Calculating accuracy by the formula = No. of correct predictions/total no. of predictions
correct_pred = 0
for i in range(len(kmeans.labels_)):
    if correct_labels[i] == kmeans.labels_[i]:
        correct_pred += 1

print("Accuarcy: "+str(correct_pred/len(kmeans.labels_)))

output-> Accuarcy: 0.9731182795698925
