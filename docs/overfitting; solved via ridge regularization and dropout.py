# -*- coding: utf-8 -*-


# In this question, we'll observe overfitting and employ ridge regularization (L2 regularization) and dropout to mitigate overfitting.

# In the following code, we load the data and define the training and test functions.
# """

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
df = pd.read_csv('bse_clean.csv', parse_dates=['Date'])
df['Day'] = df['Date'].dt.dayofweek
X = np.hstack((OneHotEncoder(sparse=False).fit_transform(df[['Hour', 'Month', 'Day']]), df[['T']])).astype('float32')
y = df[['Load']].to_numpy().astype('float32')
train_index = (df['Date'].dt.year == 2006)
test_index = ((df['Date'].dt.year >= 2007) & (df['Date'].dt.year <= 2008))
scaler_X = StandardScaler()
scaler_X.fit(X[train_index])
X = scaler_X.transform(X)
scaler_y = StandardScaler()
scaler_y.fit(y[train_index])
y = scaler_y.transform(y)
X_train = X[train_index]
X_test = X[test_index]
y_train = y[train_index]
y_test = y[test_index]

class LoadDataset(Dataset):
    def __init__(self, X, y):
        self.X, self.y = X, y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

batch_size = 128
train_dataloader = DataLoader(LoadDataset(X_train, y_train), batch_size=batch_size)
test_dataloader = DataLoader(LoadDataset(X_test, y_test), batch_size=batch_size)

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        pred = model(X)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f'loss: {loss:f}  [{current:5d}/{size:5d}]')

def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, test_mape = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            y_orig = scaler_y.inverse_transform(y)
            pred_orig = scaler_y.inverse_transform(pred)
            test_mape += np.abs((y_orig - pred_orig) / y_orig).sum()
    test_loss /= num_batches
    test_mape /= size
    print(f'Test Error: \n MAPE: {(100 * test_mape):0.2f}%, Avg loss: {test_loss:f}\n')

# """There are two hidden layers with $64$ and $32$ units, respectively, as shown below. Now changing the number of units to $1024$ and $512$, respectively. We see that the test loss decreases at the beginning, and then increases (though slowly)."""

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(44, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        x = self.fc(x)
        return x

model = NeuralNetwork()
loss_fn = nn.MSELoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-3)

epochs = 200
for t in range(epochs):
    print('Epoch', t + 1)
    print('-------------------------------')
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)
print("Done!")

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(44, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )

    def forward(self, x):
        x = self.fc(x)
        return x

model = NeuralNetwork()
loss_fn = nn.MSELoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-3)

epochs = 200
for t in range(epochs):
    print('Epoch', t + 1)
    print('-------------------------------')
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)
print("Done!")

# """
# One method to mitigate the overfitting above is to use ridge regularization (L2 regularization). set `weight_decay=0.01` in the proper function, and run the code."""

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(44, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )

    def forward(self, x):
        x = self.fc(x)
        return x

model = NeuralNetwork()
loss_fn = nn.MSELoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-3, weight_decay=0.01)

epochs = 200
for t in range(epochs):
    print('Epoch', t + 1)
    print('-------------------------------')
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)
print("Done!")

# """Another method to mitigate the overfitting above is to use dropout.Add a dropout layer with dropout rate $0.5$ after each of the two hidden layers (more specifically, after each activation function), and run the code."""

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(44, 1024),
            nn.ReLU(),
            nn.Dropout(0.5,),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.5,),
            nn.Linear(512, 1)
        )

    def forward(self, x):
        x = self.fc(x)
        return x

model = NeuralNetwork()
loss_fn = nn.MSELoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-3)

epochs = 200
for t in range(epochs):
    print('Epoch', t + 1)
    print('-------------------------------')
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)
print("Done!")
