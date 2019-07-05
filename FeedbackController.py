# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 13:40:18 2019
This is a feedback controller
@author: Marcelo
"""
from RealNetworkModel import RealNetwork
import numpy as np;
import math
import matplotlib.pyplot as plt


def controllerSimulation(xopt,yopt,nInc,random):
    
    x=[]
    ycon=[]
    memmoryPump=0
    fObjRest, Sensibil,hf = RealNetwork(xopt,0,random)

    yuncon=[]
    for inc in range(0,nInc+1):
        fObjRest, Sensibil,hf = RealNetwork(xopt,0,random)
        y=hf[inc]
        yuncon.append(y)
        if inc==nInc: break
        x.append(xopt[inc])
    
    for inc in range(1,nInc+1):
    
        fObjRest, Sensibil,hf = RealNetwork(x,0,random)
        yreal=hf[inc-1]
        ycon.append(yreal)
    
        if inc==nInc: break
        ynext=hf[inc+1]        
        disturbance=yopt[inc-1]-yreal
            #print(disturbance)
        xcorrected=xopt[inc]+disturbance/1.27
        '''
        if ynext <=2:
            x[inc]=xopt[inc]+disturbance/1.27 + 0.1
            if x[inc]>1:
                x[inc]==1
            
        elif ynext>=7:
            x[inc]=xopt[inc]+disturbance/1.27 - 0.1
            if x[inc]<0:
                x[inc]==0        
        else:
        '''
        if xcorrected >= 1:
            if xcorrected + memmoryPump > 1:
                x[inc]=1
                extraPump=xcorrected-1
                memmoryPump=memmoryPump+extraPump
            else:
                x[inc]=xcorrected+memmoryPump
                memmoryPump=0
        elif xcorrected <= 0:
            if xcorrected + memmoryPump < 0:
                x[inc]=0
                extraPump=xcorrected
                memmoryPump=memmoryPump+extraPump
            else:
                x[inc]=xcorrected+memmoryPump
                memmoryPump=0
        else:
            x[inc]=xcorrected
        if x[inc] < 0 : x[inc]=0
        if x[inc] > 1 : x[inc]=1
    
    fObjRest, Sensibil,hF = RealNetwork(x,1,random)
    ycon.append(hF[nInc])
    '''
    plt.plot(range(0,nInc),xopt,label="predicted")
    plt.plot(range(0,nInc),x,label="real")
    plt.legend()
    plt.title('curva')
    plt.xlabel('Tempo (h)')
    plt.ylabel('variação pumping')
    plt.grid()
    plt.show()
    
    plt.plot(range(0,nInc+1),yopt,label="predicted")
    plt.plot(range(0,nInc+1),yuncon,label="uncontrolled")
    plt.plot(range(0,nInc+1),ycon,label="controlled")
    plt.legend()
    plt.title('curva')
    plt.xlabel('Tempo (h)')
    plt.ylabel('variação altura')
    plt.grid()
    plt.show()
    '''
    cost=fObjRest['fObj']
    
    return x,hf,cost

def regularcontroller(x,y,nInc,random):
    
    
    
    for inc in range(0,nInc):
        
        fObjRest, Sensibil,hf = RealNetwork(x,0,random)
        havg=4.5
        disturbance=hf[inc]-havg
        xcorrect=-disturbance/1.27
        if inc==nInc-1:break
        x[inc+1]=x[inc+1]+xcorrect
        
        if x[inc+1]>=1: x[inc+1]==1
        if x[inc+1]<=0: x[inc+1]==0
        
        
    fObjRest, Sensibil,hf = RealNetwork(x,0,random)
    
    cost=fObjRest['fObj']
    
    return x,hf,cost
    
    
    