# -*- coding: utf-8 -*-
"""
Created on Mon May 13 10:39:30 2019

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
    


for i in range(1,4):
    random1.append(randint(a,b)*c)
    random2.append(randint(a,b)*c)
    ra=np.linspace(random1[i-1],random1[i],nInc/n)
    rb=np.linspace(random2[i-1],random2[i],nInc/n)
    r1=np.concatenate((r1,ra))
    r2=np.concatenate((r2,rb))

for i in range(4,7):
    random1.append(randint(a_fire,b_fire)*c)
    random2.append(randint(a_fire,b_fire)*c)
    ra=np.linspace(random1[i-1],random1[i],nInc/n)
    rb=np.linspace(random2[i-1],random2[i],nInc/n)
    r1=np.concatenate((r1,ra))
    r2=np.concatenate((r2,rb))

for i in range(7,n+1):
    random1.append(randint(a,b)*c)
    random2.append(randint(a,b)*c)
    ra=np.linspace(random1[i-1],random1[i],nInc/n)
    rb=np.linspace(random2[i-1],random2[i],nInc/n)
    r1=np.concatenate((r1,ra))
    r2=np.concatenate((r2,rb))


random=[r1,r2]
#a=randint(0,nInc-15)
a=nInc+1
miss=[a,a+10] 
print("REGULAR CONTROLLER")
plt.figure(figsize=(10,10))
fObjRest, Sensibil,y = RealNetwork(x,0,random)
x1,y1,cost0 = regularcontroller(x,y,nInc,random)
print("OPTIMAL UNCONTROLLED")
plt.figure(figsize=(10,10))
fObjRest, Sensibil,y2 = RealNetwork(xopt,0,random)
cost2=fObjRest['fObj']
'''
print("OPTIMAL FEEDBACK CONTROLLER")
plt.figure(figsize=(10,10))
x3,y3,cost3 = controllerSimulation(xopt,yopt,nInc,random)
'''
print("OPTIMAL ADAPTIVE CONTROLLER V1")
plt.figure(figsize=(10,10))
x4,y4,cost4 = AdaptiveControllerSimulation(xopt1,yopt1,nInc,random,miss)
    




a,consumo1,b=Prediction(x4,0)
c,consumo2,d=RealNetwork(x4,0,random)

#for i in range(miss[0],miss[1]): consumo2[i]=None
    
plt.figure(figsize=(15,10))
plt.plot(np.linspace(0,24,nInc),consumo1,label="Predicted Consumption")
plt.plot(np.linspace(0,24,nInc),consumo2,'k*',label="Real Consumption")
plt.legend()
plt.title('Consumptions over 24h')
plt.xlabel('Time (h)')
plt.ylabel('water comsumption(m3/s)')
plt.grid()
plt.show()

plt.figure(figsize=(15,10))
plt.plot(np.linspace(0,24,nInc),x1,label="Regular controller")
#plt.plot(np.linspace(0,24,nInc),x2,label="optimal predicted")
plt.plot(np.linspace(0,24,nInc),x2,label="optimal uncontrolled")
#plt.plot(np.linspace(0,24,nInc),x3,label="optimal feedback control")
plt.plot(np.linspace(0,24,nInc),x4,label="optimal adaptive control")
plt.legend()
plt.title('Pump Strategy')
plt.xlabel('Time (h)')
plt.ylabel('pumping amout([0:1])')
plt.grid()
plt.show()

plt.figure(figsize=(15,10))
plt.plot(np.linspace(0,24,nInc+1),y1,label="Regular controller")
#plt.plot(np.linspace(0,24,nInc+1),yopt,label="optimal predicted")
plt.plot(np.linspace(0,24,nInc+1),y2,label="optimal uncontrolled")
#plt.plot(range(0,nInc+1),y3,label="optimal feedback control")
plt.plot(np.linspace(0,24,nInc+1),y4,label="optimal adaptive control")
plt.legend()
plt.title('water level of the tank')
plt.xlabel('Time (h)')
plt.ylabel('water level(m)')
plt.grid()
plt.show()

objects = ( 'Regular controller', 'optimal uncontrolled', 'optimal adaptive control')
y_pos = np.arange(len(objects))
performance = [cost0,cost2,cost4]



plt.figure(figsize=(10,10))
bars=plt.bar(y_pos, performance, align='center', alpha=0.5)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x(), yval + 2, yval)
    
plt.xticks(y_pos, objects)
plt.ylabel('Cost')
plt.title('Cost for different control methods')

plt.show()
