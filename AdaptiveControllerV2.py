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
                    levelStep.append(best/4)

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
    #tresholdFUp=[]  
    #tresholdFDown=[] 
    
    #This loops creates the adaptation states from best to worst
    for c in range(0,len(pumpPlace[0])):
        #Create the dictionary for the current calculated option x
        AdaptationState.append(empty_AdaptationState.copy())  
        #water level without disturbance for option x
        AdaptationState[c]['TLevel']=h[pumpPlace[0][c]]
        #Upper/lower treshold for option x
       
        #tresholdFUp.append(dynamictreshold[0][pumpPlace[0][c]])
        #tresholdFDown.append(dynamictreshold[1][pumpPlace[0][c]])

        #Price Level of option x
        AdaptationState[c]['PLevel']=pumpPlace[1][c]
        #Time step of option x
        AdaptationState[c]['TimeStep']=pumpPlace[0][c]
        #Pump Planned of option x
        AdaptationState[c]['PumpBufferRemove']=x[pumpPlace[0][c]]
        #Pump in buffer of option x(basically the amount of pumping we can play with for this option)
        AdaptationState[c]['PumpBufferAdd']=1-x[pumpPlace[0][c]]
    
    #SortedDynamicTreshold=[tresholdFUp,tresholdFDown]
    
    return AdaptationState,dynamictreshold#SortedDynamicTreshold

'''
def newHight(hexpected,d,inc,Change):
        if d[inc]>0: sign=1
        else: sign=-1 
        
        for c in range(inc,len(hexpected)):
            hexpected[inc]=hexpected[inc]+d[inc]
        
        for a in range(0,len(Change[0])):
            for b in range(Change[1][a],len(hexpected)):
                hexpected[b]=hexpected[b]+sign*Change[2][a]
                
        return hexpected
'''  
    
# Starting calculations
'''
nInc = 48 #96 #24
x = [0.5 for i in range (0, nInc)]
xopt,yopt = optimalPump(x,nInc)

random1=[]
random2=[]
for i in range(0,nInc):
    random1.append(randint(-10,10))
    random2.append(randint(-10,10))
random=[random1,random2]
'''

def AdaptiveControllerSimulation2(xopt,yopt,nInc,random):
    
    nInc=len(xopt)
    fObjRest, Sensibil,h=RealNetwork(xopt,0,random)
    
    
    x=xopt
    hexpected=[]
    for i in range(0,len(yopt)):hexpected.append(yopt[i])
    
    #for loop from 0 to nInc
    d=[]
    ch=1.27
    #step 0 - Read disturbance at time step k
    for inc in range(0,nInc): 
        
        
        fObjRest, Sensibil,h=RealNetwork(x,0,random)
        disturbance=yopt[inc]-h[inc]
        
    
        for c in range(inc,len(hexpected)):
            hexpected[c]=hexpected[c]+disturbance
            
        
        #print(disturbance)
        #print(hexpected)
        #print(h)
        
    
        
        d.append(disturbance)
        #step 1 - Calculate best adaptation options
        
        AdaptationState,dynamictreshold=AdaptationOptions(hexpected,inc,x) #,disturbance)
        
        #print(inc)
        #print('\n')
        #print(treshold)
        #step 2 - Simulate adaptation Options
           
        xcorrect=abs(disturbance/ch)
        
        
        
       
        #This will find the time step where the treshold is negative or minimum in case there is no negative
        #Maybe here it's necessary to find the diferent intervals and not just the first one
        
        positionUp=nInc
        positionDown=nInc
        
            
        tresholdUp=0
        tresholdDown=0
        
        tup=0
        tdown=0
    
        for i in range(0, len(dynamictreshold[1])):
            if dynamictreshold[1][i] < 0:
                positionDown=i
                tresholdDown=dynamictreshold[1][i]
                
            
        for i in range(0, len(dynamictreshold[0])):
            if dynamictreshold[0][i] < 0 :
                positionUp=i
                tresholdUp=dynamictreshold[0][i]
                
            
        if tresholdUp<0: tup=1
        if tresholdDown<0: tdown=1
        #print(positionUp)
        #Posso adicionar entre o timestepUp e o timestepDown e retirar no resto do intervalo
    
        Adaptation=[]
        Step=[]
        hightChange=[]
        #Neste intervalo posso adicionar e a melhor opção começa no valor  0 e piora quando aumenta
        #print('posso adicionar')
        for c in range(1,len(AdaptationState)+1):
            
            if xcorrect==0: break
        
            if disturbance > 0 :
                #take
                if tdown==1:
                    #take up to treshold down before position down
                    if AdaptationState[c-1]['TimeStep']<positionDown:
                        #take on time steps before positionDOwn
                        if abs(xcorrect)>AdaptationState[c-1]['PumpBufferAdd'] and dynamictreshold[1][AdaptationState[c-1]['TimeStep']]<AdaptationState[c-1]['PumpBufferAdd']*ch:
                            xcorrect=xcorrect-AdaptationState[c-1]['PumpBufferAdd']
                            disturbance=disturbance-AdaptationState[c-1]['PumpBufferAdd']*ch
                            Adaptation.append(AdaptationState[c-1]['PumpBufferAdd'])
                            Step.append(AdaptationState[c-1]['TimeStep'])
                            hightChange.append(AdaptationState[c-1]['PumpBufferAdd']*ch)
                        elif abs(xcorrect)<=AdaptationState[c-1]['PumpBufferAdd'] and dynamictreshold[1][AdaptationState[c-1]['TimeStep']]<AdaptationState[c-1]['PumpBufferAdd']*ch:
    
                            Adaptation.append(xcorrect)
                            Step.append(AdaptationState[c-1]['TimeStep'])
                            hightChange.append(AdaptationState[c-1]['PumpBufferAdd']*ch)
                            xcorrect=0
                            disturbance=0
                else:
                    #take up the disturbance wherever is best
                    if abs(xcorrect)>AdaptationState[c-1]['PumpBufferAdd'] and dynamictreshold[1][AdaptationState[c-1]['TimeStep']]<AdaptationState[c-1]['PumpBufferAdd']*ch:
                        xcorrect=xcorrect-AdaptationState[c-1]['PumpBufferAdd']
                        disturbance=disturbance-AdaptationState[c-1]['PumpBufferAdd']*ch
                        Adaptation.append(AdaptationState[c-1]['PumpBufferAdd'])
                        Step.append(AdaptationState[c-1]['TimeStep'])
                        hightChange.append(AdaptationState[c-1]['PumpBufferAdd']*ch)
                    elif abs(xcorrect)<=AdaptationState[c-1]['PumpBufferAdd'] and dynamictreshold[1][AdaptationState[c-1]['TimeStep']]<AdaptationState[c-1]['PumpBufferAdd']*ch :
    
                        Adaptation.append(xcorrect)
                        Step.append(AdaptationState[c-1]['TimeStep'])
                        hightChange.append(AdaptationState[c-1]['PumpBufferAdd']*ch)
                        xcorrect=0
                        disturbance=0
            else:
                
                if tup==1:
                    #give to treshold Up
                    if AdaptationState[-c]['TimeStep']<positionUp:
                        #give only on timesteps before posiition up
                        if abs(xcorrect)>AdaptationState[-c]['PumpBufferRemove'] and dynamictreshold[0][AdaptationState[-c]['TimeStep']]<AdaptationState[-c]['PumpBufferRemove']*ch :
                            xcorrect=xcorrect-AdaptationState[-c]['PumpBufferRemove']
                            disturbance=disturbance-AdaptationState[-c]['PumpBufferRemove']*ch
                            Adaptation.append(-AdaptationState[-c]['PumpBufferRemove'])
                            Step.append(AdaptationState[-c]['TimeStep'])
                            hightChange.append(-AdaptationState[-c]['PumpBufferRemove']*ch)
                        elif abs(xcorrect)<=AdaptationState[-c]['PumpBufferRemove'] and dynamictreshold[0][AdaptationState[-c]['TimeStep']]<AdaptationState[-c]['PumpBufferRemove']*ch:
                            Adaptation.append(-xcorrect)
                            Step.append(AdaptationState[-c]['TimeStep'])
                            hightChange.append(-AdaptationState[-c]['PumpBufferRemove']*ch)
                            xcorrect=0
                            disturbance=0
                        
                    
                else:
                    #give wherever is best
                    if abs(xcorrect)>AdaptationState[-c]['PumpBufferRemove'] and dynamictreshold[0][AdaptationState[-c]['TimeStep']]<AdaptationState[-c]['PumpBufferRemove']*ch :
                        xcorrect=xcorrect-AdaptationState[-c]['PumpBufferRemove']
                        disturbance=disturbance-AdaptationState[-c]['PumpBufferRemove']*ch
                        Adaptation.append(-AdaptationState[-c]['PumpBufferRemove'])
                        Step.append(AdaptationState[-c]['TimeStep'])
                        hightChange.append(-AdaptationState[-c]['PumpBufferRemove']*ch)
                    elif abs(xcorrect)<=AdaptationState[-c]['PumpBufferRemove'] and dynamictreshold[0][AdaptationState[-c]['TimeStep']]<AdaptationState[-c]['PumpBufferRemove']*ch:
                        Adaptation.append(-xcorrect)
                        Step.append(AdaptationState[-c]['TimeStep'])
                        hightChange.append(-AdaptationState[-c]['PumpBufferRemove']*ch)
                        xcorrect=0
                        disturbance=0
        
          
        Change=[Adaptation,Step,hightChange]
            
        for c in range(0,len(Change[0])):
            x[Change[1][c]]=x[Change[1][c]]+Change[0][c]
            for b in range(Change[1][c],len(hexpected)):
                hexpected[b]=hexpected[b]+Change[2][c]      
        
        
        
        
       
                
                #hexpected[Change[1][c]]=hexpected[Change[1][c]]-Change[2][c]
            
            
        #if hexpected[inc+1]>6.5 and inc<47: x[inc+1]=0
        #if hexpected[inc+1]<2.5 and inc<47: x[inc+1]=1
        
        
        
            
        #Step 3 - To adapt or to not adapt
        
        #print(Change)
        #Step 4 - Give the new Pumping intructions to the controller
        
        #print(AdaptationState)
    
    
    fObjRest, Sensibil,hFinal= RealNetwork(x,1,random)

    return hFinal,x