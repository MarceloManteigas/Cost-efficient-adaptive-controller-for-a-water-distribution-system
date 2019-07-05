# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:05:29 2019
third version of the adaptive controller
@author: Marcelo
"""
import matplotlib.pyplot as plt
import numpy as np
from PredictionModel import optimalPump



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

nInc=48

Price=PricePyramic(nInc)


x = [0.5 for i in range (0, nInc)]
xopt,yopt,A,B,t = optimalPump(x,nInc)

inc=0

h=yopt
d=0
for i in range(0,len(h)):
    h[i]=h[i]+d
  

def HiearchyPump(h,inc):
    hInc=h[inc:len(h)]
    hsorted=np.argsort(hInc)
    for i in range(0,len(hsorted)):
        hsorted[i]=hsorted[i]+inc
        
    return hsorted


hSortedSteps=HiearchyPump(h,inc)
#print(hSortedSteps)
hSorted=[]

for i in range(0,len(hSortedSteps)):
    hSorted.append(h[hSortedSteps[i]])
   
#print(hSorted)
plt.figure(figsize=(15,10))
plt.rcParams.update({'font.size': 18})
plt.plot(Price[0][0],[Price[0][1]*15]*len(Price[0][0]),'bo',label='level1')
plt.plot(Price[1][0],[Price[1][1]*15]*len(Price[1][0]),'ro',label='level2')
plt.plot(Price[2][0],[Price[2][1]*15]*len(Price[2][0]),'yo',label='level3')
plt.plot(Price[3][0],[Price[3][1]*15]*len(Price[3][0]),'go',label='level4')

plt.plot(hSortedSteps,hSorted,'b+',label='WaterLevel')


def BestPumpOptions(hsorted,Price):
        
    bestStep=[]
    levelStep=[] 
    best=nInc
    a=len(Price)
    b=len(hsorted)
    for z in range(0,a):
        for y in range(0,b):
            if hsorted[y] in Price[z][0]:
                best=best-1
                bestStep.append(hsorted[y])
                levelStep.append(best/6)
            #print(where)
    pumpOptions=[bestStep,levelStep]
    return pumpOptions

pumpOptions=BestPumpOptions(hSortedSteps,Price)

x=xopt

plt.plot(pumpOptions[0],pumpOptions[1],'k*',label='BestOptions')
plt.scatter(pumpOptions[0][-1],pumpOptions[1][-1], s=400, marker='o',label='BestOption')
plt.title('Hierarchy Update Control')
plt.xlabel('Control Increments(k)')
plt.legend()
plt.show()


def DynamicTreshold(h):
    htreshup=[7]*len(h)
    thresholdUp= [htreshup[i]-h[i] for i in range(0,len(h))]
    htreshdown=[2]*len(h)
    thresholdDown= [h[i]-htreshdown[i] for i in range(0,len(h))]             
        
    dynamictreshold=[thresholdUp,thresholdDown]
    return dynamictreshold

dynamictreshold=DynamicTreshold(h)

'''
tresholdFUp=[]
tresholdFDown=[]
for c in range(0,len(pumpOptions[0])):
    tresholdFUp.append(dynamictreshold[0][pumpOptions[0][c]])
    tresholdFDown.append(dynamictreshold[1][pumpOptions[0][c]])
'''
tresholdUp=0
tresholdDown=0
positionDown=nInc
positionUp=nInc


for i in range(0, len(dynamictreshold[1])):
    if dynamictreshold[1][i] < 0:
        positionDown=i
        tresholdDown=dynamictreshold[1][i]
        break
        
for i in range(0, len(dynamictreshold[0])):
    if dynamictreshold[0][i] < 0 :
        positionUp=i
        tresholdUp=dynamictreshold[0][i]
        break


plt.plot(hSortedSteps,hSorted,'b+',label='WaterLevel')
plt.plot(range(inc,nInc+1),dynamictreshold[0][inc:nInc+1],'r+',label='tresholdUp')
plt.plot(range(inc,nInc+1),dynamictreshold[1][inc:nInc+1],'g+',label='tresholdDown')
plt.scatter(positionUp,h[positionUp], s=200, marker='o')
plt.scatter(positionDown,h[positionDown], s=200, marker='^')

plt.show()








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
for c in range(0,len(pumpOptions[0])):
        #Create the dictionary for the current calculated option x
    AdaptationState.append(empty_AdaptationState.copy())  
        #water level without disturbance for option x
    AdaptationState[c]['TLevel']=h[pumpOptions[0][c]]
        #Upper/lower treshold for option x
       
    tresholdFUp.append(dynamictreshold[0][pumpOptions[0][c]])
    tresholdFDown.append(dynamictreshold[1][pumpOptions[0][c]])

        #Price Level of option x
    AdaptationState[c]['PLevel']=pumpOptions[1][c]
        #Time step of option x
    AdaptationState[c]['TimeStep']=pumpOptions[0][c]
        #Pump Planned of option x
    AdaptationState[c]['PumpBufferRemove']=x[pumpOptions[0][c]]
        #Pump in buffer of option x(basically the amount of pumping we can play with for this option)
    AdaptationState[c]['PumpBufferAdd']=1-x[pumpOptions[0][c]]
    
SortedDynamicTreshold=[tresholdFUp,tresholdFDown]

print(AdaptationState[0])

