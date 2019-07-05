# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 15:09:50 2019

@author: Marcelo
"""
from RealNetworkModel import RealNetwork
from PredictionModel import optimalPump

import numpy as np
import matplotlib.pyplot as plt
from random import randint


'''
This function takes in the current increment the expected water tank level predicted and the disturbance and the pump 
amount over 24 hours, and outputs the best adaptation options at each time step
'''
def AdaptationOptions(h,inc,x):
    
    '''
    This function takes in the number of increments and outputs a price stucture with the levels of prices
    from 1 to 4, each level containing a list of the increments at which is that given price
    '''
    nInc=len(x)
    def PricePyramic(nInc):
    
        def tarifario(ti):
            # definição do tarifário usando o tempo inicial do incremento
            tarifHora = [None]*7; tarifCusto = [None]*7;
            set(tarifHora)
            tarifHora[0]= 0; tarifCusto[0]= 0.0737
            tarifHora[1]=2; tarifCusto[1]= 0.06618
            tarifHora[2]=6; tarifCusto[2]=  0.0737
            tarifHora[3]=7; tarifCusto[3]=  0.10094
            tarifHora[4]=9; tarifCusto[4]=  0.18581
            tarifHora[5]=12; tarifCusto[5]= 0.10094
            tarifHora[6]=24; tarifCusto[6]= 0.10094
            tarifF = 0.
            for i in range(0, len(tarifHora)-1):
                if (ti >= tarifHora[i]) & (ti < tarifHora[i+1]):
                    tarifF = tarifCusto[i]
                
            if tarifF == 0.06618: level='level1'
            if tarifF == 0.0737: level='level2'
            if tarifF == 0.10094: level='level3'
            if tarifF == 0.18581: level='level4'
              
            if tarifF == 0.: print("Erro no tarifário",ti,i); quit()
            return tarifF,level
     
    
        positions1=[]
        positions2=[]
        positions3=[]
        positions4=[]
        
        for ti in range(0,nInc):
            
            tariF,level=tarifario(ti*24/nInc)
            if level=="level1": positions1.append(ti)
            if level=="level2": positions2.append(ti)
            if level=="level3": positions3.append(ti)
            if level=="level4": positions4.append(ti)
            
        level1=[positions1,0.06618]
        level2=[positions2,0.0737 ]
        level3=[positions3,0.10094]
        level4=[positions4,0.18581]
        
        Price=[level1,level2,level3,level4]
        
        return Price
    
    '''
    This function accepts the array of high and the current increment and ouputs an array with the sorted time steps
    of the high over 24h from the smallest to the highest
    '''
    #def HiearchyPump(h,inc):
        #hsorted=np.argsort(h[inc:len(h)])
        #return hsorted
    
    def HiearchyPump(h,inc):
        hInc=h[inc:len(h)]
        hsorted=np.argsort(hInc)
        for i in range(0,len(hsorted)):
            hsorted[i]=hsorted[i]+inc
        
        return hsorted
    
    '''
    This function takes in the Price pyramid and the water tank level pyramid and outputs the best pump obtions
    from best to worst, by matching the lowest price time steps with the lowest water tank level
    '''
    
    def BestPumpOptions(hsorted,Price):
        
        bestStep=[]
        levelStep=[] 
        best=0
        a=len(Price)
        b=len(hsorted)
        for z in range(0,a):
            for y in range(0,b):
                if hsorted[y] in Price[z][0]:
                    best=best+1
                    bestStep.append(hsorted[y])
                    levelStep.append(best)

        pumpOptions=[bestStep,levelStep]
        return pumpOptions
    

    Price=PricePyramic(nInc)
    hsorted=HiearchyPump(h,inc)
    pumpPlace=BestPumpOptions(hsorted,Price)    
    #print(pumpPlace)
    #print(len(hsorted))
    
    '''
    This function takes in the water level of the tank and the current increment and outputs the treshold of the upper
    and lower bond of the tank that differs at every increment
    '''
    def DynamicTreshold(h):
        htreshup=[7]*len(h)
        thresholdUp= [htreshup[i]-h[i] for i in range(0,len(h))]
        htreshdown=[2]*len(h)
        thresholdDown= [h[i]-htreshdown[i] for i in range(0,len(h))]             
        
        dynamictreshold=[thresholdUp,thresholdDown]
        return dynamictreshold
    
    dynamictreshold=DynamicTreshold(h)
    
    # definição dos dicionários
    empty_AdaptationState = {
            'TLevel': None,
            'PLevel': None,
            'TimeStep': None, 
            'PumpBufferRemove': None,
            'PumpBufferAdd': None,};
    # Create the list to hold the dictionaries   
    AdaptationState=[]
    tresholdFUp=[]  
    tresholdFDown=[] 
    
    #This loops creates the adaptation states from best to worst
    for c in range(0,len(pumpPlace[0])):
        #Create the dictionary for the current calculated option x
        AdaptationState.append(empty_AdaptationState.copy())  
        #water level without disturbance for option x
        AdaptationState[c]['TLevel']=h[pumpPlace[0][c]]
        #Upper/lower treshold for option x
       
        tresholdFUp.append(dynamictreshold[0][pumpPlace[0][c]])
        tresholdFDown.append(dynamictreshold[1][pumpPlace[0][c]])

        #Price Level of option x
        AdaptationState[c]['PLevel']=pumpPlace[1][c]
        #Time step of option x
        AdaptationState[c]['TimeStep']=pumpPlace[0][c]
        #Pump Planned of option x
        AdaptationState[c]['PumpBufferRemove']=x[pumpPlace[0][c]]
        #Pump in buffer of option x(basically the amount of pumping we can play with for this option)
        AdaptationState[c]['PumpBufferAdd']=1-x[pumpPlace[0][c]]
    
    SortedDynamicTreshold=[tresholdFUp,tresholdFDown]
    
    return AdaptationState,SortedDynamicTreshold

def Contraint_Validation(constraint_k,hexpected,inc,nInc,x,ch):
    
    if constraint_k>0:
        constraint_buffer=0.3
        if constraint_k>=6:constraint_buffer=0.6
        elif constraint_k>=9:constraint_buffer=0.8
    elif constraint_k<0:
        constraint_buffer=-0.3
        if constraint_k<=-6:constraint_buffer=-0.6
        elif constraint_k<=-9:constraint_buffer=-0.8
    else:constraint_buffer=0
    
    a=0
        
    if hexpected[inc]>=6.4+constraint_buffer and inc+1<nInc:
        a=abs(hexpected[inc]-(6.4+constraint_buffer))/ch
                
        if x[inc+1]<=a:
            a=x[inc+1]
            x[inc+1]=0
            
        else:
            x[inc+1]=x[inc+1]-a
            
        a=-a     
        
    if hexpected[inc]<=2.6+constraint_buffer and inc+1<nInc : 
        a=abs((2.6+constraint_buffer)-hexpected[inc])/ch
        if (1-x[inc+1])>=a:
            x[inc+1]=x[inc+1]+a
            
        else:
            a=1-x[inc+1]
            x[inc+1]=1
            
    
    for c in range(inc,len(hexpected)-1):
        hexpected[c+1]=hexpected[c+1]+a*ch
            
    
    
    return hexpected,x
   
def treshold_rectifier(treshold,inc,nInc):
            
    timestepDown=nInc-inc
    timestepUp=nInc-inc
     
    tresholdup=0
    tresholddown=0
           
    for i in range(0,len(treshold[0])):
        if treshold[0][i]<=0:
            if tresholdup<abs(treshold[0][i]):
                tresholdup=abs(treshold[0][i])
                timestepUp=i
        if treshold[1][i]<=0: 
            if tresholddown<abs(treshold[1][i]):
                tresholddown=abs(treshold[1][i])
                timestepDown=i
           
    return timestepUp,timestepDown


def dynamic_search(disturbance,AdaptationState,treshold,x,hexpected,constraint_k,timestepDown,timestepUp,ch):
    #amount of pumping time to correct based on the measured distubance

    xcorrect=abs(-disturbance/ch)
        
    Adaptation=[]
    Step=[]
    hightChange=[]
       
    if disturbance > 0:
        
        constraint_k=constraint_k+1
            
        for c in range(0,len(AdaptationState)):
                
            if xcorrect==0: break
            
            if (AdaptationState[c]['TimeStep']<timestepDown):
                if treshold[1][AdaptationState[c]['TimeStep']]<AdaptationState[c]['PumpBufferAdd']*ch and xcorrect>=AdaptationState[c]['PumpBufferAdd']:
                    xcorrect=xcorrect-AdaptationState[c]['PumpBufferAdd']
                    Adaptation.append(AdaptationState[c]['PumpBufferAdd'])
                    Step.append(AdaptationState[c]['TimeStep'])
                    disturbance=disturbance-AdaptationState[c]['PumpBufferAdd']*ch
                    hightChange.append(AdaptationState[c]['PumpBufferAdd']*ch)
    
                elif treshold[1][AdaptationState[c]['TimeStep']]>=abs(disturbance) and AdaptationState[c]['PumpBufferAdd']>=xcorrect:
                    Adaptation.append(xcorrect)
                    hightChange.append(xcorrect*ch)
                    xcorrect = 0
                    disturbance = 0
                    Step.append(AdaptationState[c]['TimeStep'])

                
        Change=[Adaptation,Step,hightChange]
            
        
        for c in range(0,len(Change[0])):
            x[Change[1][c]]=x[Change[1][c]]+Change[0][c]
            for b in range(Change[1][c],len(hexpected)):
                hexpected[b]=hexpected[b]+Change[2][c]

    else:  
            
        constraint_k=constraint_k-1
            
        for c in range(1,len(AdaptationState)+1):
                
            if xcorrect<=0: break
            if (AdaptationState[-c]['TimeStep']<timestepUp):
                if treshold[0][AdaptationState[-c]['TimeStep']]<AdaptationState[-c]['PumpBufferRemove']*ch and xcorrect>=AdaptationState[-c]['PumpBufferRemove']:
                    xcorrect=xcorrect-AdaptationState[-c]['PumpBufferRemove']
                    Adaptation.append(AdaptationState[-c]['PumpBufferRemove'])
                    Step.append(AdaptationState[-c]['TimeStep'])
                    disturbance=disturbance-AdaptationState[-c]['PumpBufferRemove']*ch
                    hightChange.append(AdaptationState[-c]['PumpBufferRemove']*ch)
                        
                elif treshold[0][AdaptationState[-c]['TimeStep']]>=abs(disturbance) and AdaptationState[-c]['PumpBufferRemove']>=xcorrect:
                    Adaptation.append(xcorrect)
                    hightChange.append(xcorrect*ch)
                    xcorrect = 0
                    disturbance = 0
                    Step.append(AdaptationState[-c]['TimeStep'])
                
        
        Change=[Adaptation,Step,hightChange]
            
            #updating puping strategy and the expected water level 
        for c in range(0,len(Change[0])):
            x[Change[1][c]]=x[Change[1][c]]-Change[0][c]
            for b in range(Change[1][c],len(hexpected)):
                hexpected[b]=hexpected[b]-Change[2][c]
                    
                
    return x,hexpected,constraint_k,disturbance




def AdaptiveControllerSimulation(xopt,yopt,nInc,random,miss):
    
    #Initiate Variables
    constraint_k=0
    ch=1.27
    x=[]
    hexpected=[]
    for i in range(0,len(xopt)):x.append(xopt[i])
    for i in range(0,len(yopt)):hexpected.append(yopt[i])
    a=0
    disturbance=0
    for inc in range(0,nInc): 
        #calculating the disturbance based on comparing the real readings of water level and the optimized predition 
        fObjRest, Sensibil,h=RealNetwork(x,0,random)
        
        if inc>=miss[0] and inc<=miss[1]: h==None
        
        if h==None: 
            a=a+1
            pass
        else:
            hexpected[inc-a:inc]=h[inc-a:inc]
            a=0
    
        disturbance=disturbance+yopt[inc]-h[inc]
        #updating the vector describing the expected water level over the 24 hour period
        hexpected[inc]=h[inc]
        for c in range(inc,len(hexpected)-1):
            hexpected[c+1]=hexpected[c+1]+disturbance
        #calculation of the array with the sorted best adaptation options
        AdaptationState,treshold=AdaptationOptions(hexpected,inc,x)
        #calculationg of the time steps before which the system must adapt to validate the constraints
        timestepUp,timestepDown=treshold_rectifier(treshold,inc,nInc)
        #Dynamic search algorithm, based on the disturbance and the sorted list of best adaptation options, 
        #nulifies the distubance on the most cost efficient way
        x,hexpected,constraint_k,disturbance=dynamic_search(disturbance,AdaptationState,treshold,x,hexpected,constraint_k,timestepDown,timestepUp,ch)
        #validatiion of constraints based on the expected water level and trend of water 
        #comsumption, by tweaking the pumping time in the following increment
        hexpected,x=Contraint_Validation(constraint_k,hexpected,inc,nInc,x,ch)
 
    fObjRest, Sensibil,hFinal = RealNetwork(x,0,random)
    cost=fObjRest['fObj']
    
    return x,hFinal,cost

