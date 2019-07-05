# -*- coding: utf-8 -*-
"""
This is the simulation of the controller

@author: Marcelo
"""
from PredictionModel import optimalPump
from PredictionModel import Prediction
from FeedbackController import controllerSimulation
from FeedbackController import regularcontroller
from random import randint
import numpy as np;
from AdaptiveController import AdaptiveControllerSimulation
from RealNetworkModel import RealNetwork
import matplotlib.pyplot as plt
import pickle

# main program (driver)
#----------------------
nInc = 96 #96 #24
# Declaração de solução
x = [0.5 for i in range (0, nInc)]
'''
xopt,yopt,xopt1,yopt1,cost1 = optimalPump(x,nInc)


with open('xopt.pickle', 'wb') as output:
    pickle.dump(xopt, output)
    
with open('yopt.pickle', 'wb') as output:
    pickle.dump(yopt, output)
    
with open('cost1.pickle', 'wb') as output:
    pickle.dump(cost1, output)
'''
c_c=[]
c_u=[]
c_r=[]
cost_c=[]
cost_u=[]
cost_r=[]

N=1000

for ite in range(0,N):

    with open('xopt.pickle', 'rb') as data:
        xopt = pickle.load(data)
        
    with open('yopt.pickle', 'rb') as data:
        yopt = pickle.load(data)
    
    with open('cost1.pickle', 'rb') as data:
        cost1 = pickle.load(data)
    
    xopt= list(np.around(np.array(xopt),2))
    
    xopt1=[]
    for i in range(0,len(xopt)): xopt1.append(xopt[i]) 
    
    yopt1=[]
    for i in range(0,len(yopt)): yopt1.append(yopt[i]) 
    
    x2=[]
    for i in range(0,len(xopt)): x2.append(xopt[i]) 
    
    x = [0.5 for i in range (0, nInc)]
    
    a=-1000
    b=1000
    c=0.001
    n=8

    a_fire=5000
    b_fire=8000

    random1=[]
    random2=[]
    random1.append(randint(a,b)*c)
    random2.append(randint(a,b)*c)
    r1=[]
    r2=[]
    


    for i in range(1,n+1):
        random1.append(randint(a,b)*c)
        random2.append(randint(a,b)*c)
        ra=np.linspace(random1[i-1],random1[i],nInc/n)
        rb=np.linspace(random2[i-1],random2[i],nInc/n)
        r1=np.concatenate((r1,ra))
        r2=np.concatenate((r2,rb))
    


    random=[r1,r2]
    a=randint(0,nInc-15)
    #a=nInc+1
    miss=[a,a+10] 
    plt.figure(figsize=(10,10))
    fObjRest, Sensibil,y = RealNetwork(x,0,random)
    x1,y1,cost0 = regularcontroller(x,y,nInc,random)
    
    fObjRest, Sensibil,y2 = RealNetwork(xopt,0,random)
    cost2=fObjRest['fObj']
    
    x4,y4,cost4 = AdaptiveControllerSimulation(xopt1,yopt1,nInc,random,miss)
    
    cost_c.append(cost4)
    cost_u.append(cost2)
    cost_r.append(cost0)
    
    constraint_c=1
    constraint_u=1
    constraint_r=1
    
    for inc in range(0,nInc):
        if y4[inc]>7 or y4[inc]<2:
            constraint_c=0
            break
        
    c_c.append(constraint_c)  
    
    for inc in range(0,nInc):
        if y2[inc]>7 or y2[inc]<2:
            constraint_u=0
            break
    c_u.append(constraint_u) 

    for inc in range(0,nInc):
        if y1[inc]>7 or y1[inc]<2:
            constraint_r=0
            break
        
    c_r.append(constraint_r) 




plt.figure(figsize=(10,10))

objects = ( 'regular controller', 'optimal strategy controller', 'optimal adaptive controller')
y_pos = np.arange(len(objects))
performance = [sum(c_r),sum(c_u),sum(c_c)]
performance2 =[sum(cost_r)/N,sum(cost_u)/N,sum(cost_c)/N]

bars=plt.bar(y_pos, performance, align='center', alpha=0.5)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x(), yval + 10, yval/N)
    #print("accuraccy = {}".format( yval/N))
    
plt.xticks(y_pos, objects)
plt.ylabel('Nº of sucessful controls')
plt.title('sucessful controls')

plt.show()

plt.figure(figsize=(10,10))

bars2=plt.bar(y_pos, performance2, align='center', alpha=0.5)
for bar2 in bars2:
    yval = bar2.get_height()
    plt.text(bar2.get_x(), yval + 4, yval)
    #print("accuraccy = {}".format( yval/N))
    
plt.xticks(y_pos, objects)
plt.ylabel('Cost')
plt.title('Average Cost')

plt.show()



a,consumo1,b=Prediction(x4,0)
c,consumo2,d=RealNetwork(x4,0,random)

for i in range(miss[0],miss[1]): consumo2[i]=None

plt.figure(figsize=(15,10))
plt.plot(np.linspace(0,24,nInc),consumo1,label="Predicted Consumption")
plt.plot(np.linspace(0,24,nInc),consumo2,'*k',label="Real Consumption")
plt.legend()
plt.title('Consumptions over 24h')
plt.xlabel('Time (h)')
plt.ylabel('water comsumption(m3/s)')
plt.grid()
plt.show()

plt.figure(figsize=(15,10))
plt.plot(np.linspace(0,24,nInc),x1,label="Regular controller")
plt.plot(np.linspace(0,24,nInc),x2,label="optimal predicted")
plt.plot(np.linspace(0,24,nInc),x2,label="optimal uncontrolled")
#plt.plot(np.linspace(0,24,nInc),x3,label="optimal feedback control")
plt.plot(np.linspace(0,24,nInc),x4,label="optimal adaptive control")
plt.legend()
plt.title('water level of the tank')
plt.xlabel('Time (h)')
plt.ylabel('pumping amout([0:1])')
plt.grid()
plt.show()

plt.figure(figsize=(15,10))
plt.plot(range(0,nInc+1),y1,label="Regular controller")
plt.plot(range(0,nInc+1),yopt,label="optimal predicted")
plt.plot(range(0,nInc+1),y2,label="optimal uncontrolled")
#plt.plot(range(0,nInc+1),y3,label="optimal feedback control")
plt.plot(range(0,nInc+1),y4,label="optimal adaptive control")
plt.legend()
plt.title('water level of the tank')
plt.xlabel('Time (h)')
plt.ylabel('water level(m)')
plt.grid()
plt.show()

objects = ( 'regultar controller', 'optimal uncontrolled', 'optimal adaptive control')
y_pos = np.arange(len(objects))
performance = [cost0,cost2,cost4]



plt.figure(figsize=(10,10))
plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Cost')
plt.title('Cost for different control methods')

plt.show()
