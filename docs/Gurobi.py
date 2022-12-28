# -*- coding: utf-8 -*-
# """git-mod hw4.ipynb

# Automatically generated by Colaboratory.

# Original file is located at
#     https://colab.research.google.com/drive/1iq3QXBg37V2JvFk2-aaSHfTxZZOK4FyE

# In this assignment, we will use Gurobi to solve a DC optimal power flow (OPF) problem while determining the locational marginal prices (LMPs) simultaneously, for the [modified PJM 5-bus system](https://doi.org/10.1109/PES.2010.5589973).
# """


# """The DC OPF problem is formulated as a linear programming problem:

# %pip install gurobipy

import numpy as np
import gurobipy as gp
from gurobipy import GRB

# set p_min, p_max, mc, f_max, W_prime, d_prime, H, A_prime, B_prime, S_prime, S
p_min = np.array([0,0,0,0,0]).transpose()
p_max = np.array([40,170,520,200,600]).transpose()
mc = np.array([14,15,30,40,10]).transpose()
f_max = np.array([400, GRB.INFINITY, GRB.INFINITY, GRB.INFINITY, GRB.INFINITY, 240]).transpose()

W = np.array([ [1,1,0,0,0], [0,0,0,0,0], [0,0,1,0,0], [0,0,0,1,0], [0,0,0,0,1] ])
# W_prime =  np.array([ [1,1,0,0,0], [0,0,0,0,0], [0,0,1,0,0], [0,0,0,0,1]])
# dropping the fourth row to find the prime W_prime
W_prime = np.delete(W, 3, 0)
d = np.array([0,300,300,400,0]).transpose()
d_prime = np.array([0,300,300,0]).transpose()

LR = np.array([0.0281,0.0304,0.0064,0.0108,0.0297,0.0297])
LR_reciprocal = np.reciprocal(LR)
H = np.diag(LR_reciprocal)

A = np.array([ [1,-1,0,0,0], [1,0,0,-1,0], [1,0,0,0,-1], [0,1,-1,0,0], [0,0,1,-1,0], [0,0,0,1,-1]])
# A_prime = np.array([ [1,-1,0,0], [1,0,0,0], [1,0,0,-1], [0,1,-1,0], [0,0,1,0], [0,0,0,-1]])
# dropping the fourth column to find the prime A_prime
A_prime = np.delete(A, 3, 1)

B_prime = A_prime.transpose() @ H @ A_prime
S_prime = H @ A_prime @ np.linalg.inv(B_prime)

# 𝑆 is obtained by adding zero column corresponding to the slack bus(4th column) from 𝑆′
S = np.insert(S_prime, 3, np.zeros(6), axis=1)

# checking dimensions of all matrices 
print(H.shape)
print(A_prime.shape)
print(B_prime.shape)
print(S_prime.shape)
print(W_prime.shape)
print((S_prime @ W_prime).shape)
print((S_prime @ W_prime @ d).shape)

m = gp.Model()
m.Params.LogToConsole = 0
p = m.addMVar(5, lb=p_min, ub=p_max, obj=mc, name='p')
m.modelSense = GRB.MINIMIZE
m.setObjective( mc.transpose() @ p )
c_lambda = m.addConstr(np.ones(5).transpose() @ d == np.ones(5).transpose() @ p)
c_mu = m.addConstr( -S_prime @ W_prime @ p >= -S_prime @ d_prime - f_max )
c_nu = m.addConstr( S_prime @ W_prime @ p >= S_prime @ d_prime - f_max )
m.optimize()

# print optimal dispatch p 
if (m.status == GRB.OPTIMAL):
    for var in m.getVars():
        print(var.varName, var.x)

# print optimal value of the objective function
print(m.objVal)

# print the LMP energy component 
p =  m.getAttr('x', m.getVars())
print(c_lambda.pi * np.ones(5))

# print the LMP congestion components 
print(S.transpose() @ (c_nu.pi - c_mu.pi))

# print the LMPs 
# pi = energy component + congestion components
print(c_lambda.pi * np.ones(5) + S.transpose() @ (c_nu.pi - c_mu.pi))

# print the line flows 
# from 𝑆′(𝑊′𝑝−𝑑′)≤𝑓max 
print(S_prime @ (W_prime @ p - d_prime))
