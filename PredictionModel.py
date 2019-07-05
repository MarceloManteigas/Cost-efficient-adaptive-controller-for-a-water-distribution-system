# -*- coding: utf-8 -*-
"""
This files will be used to produce a "prediction" an optimal operational 
schedule of the pumps
@author: Marcelo
"""

import numpy as np;
import math
import matplotlib.pyplot as plt
from scipy.optimize import Bounds
from scipy.optimize import LinearConstraint
from scipy.optimize import NonlinearConstraint
from scipy.optimize import BFGS
from scipy.optimize import minimize
from scipy.optimize import linprog

def Prediction(x,iChart):
    nInc = len(x)
    # definição dos dicionários
    empty_timeIncrem = {
        'number': None,
        'startTime': None, 'duration': None,'endTime': None,
        'hFini': None, 'hFfin': None,};
    fObjRest = {'fObj': None, 'g1': [], 'g2': []}
    Sensibil = {'dCdx': [],'dg1dx': [[0 for j in range(nInc)]for i in range(nInc)],
                'dg2dx': [[0 for j in range(nInc)]for i in range(nInc)]};

    y=[]
    consumo=[]
    # Cálculo dos consumos em cada t
    def Caudal_VC(ti, tf):
        # definição do polinómio
        a6 = -5.72800E-05; a5 = 3.9382E-03; a4=-9.8402E-02
        a3 = 1.0477; a2 = -3.8621; a1 = -1.1695; a0 = 7.53930E+01
        QVC = a6/7.*(tf**7.-ti**7.)+a5/6.*(tf**6.-ti**6.)+a4/5.*(tf**5.-ti**5.)+ a3/4.*(tf**4.-ti**4.)+a2/3.*(tf**3.-ti**3.)+a1/2.*(tf**2.-ti**2.)+a0*(tf-ti)
        return QVC

    def Caudal_R(ti, tf):
        # definição do polinómio
        a3 = -0.004; a2 = 0.09; a1 = 0.1335; a0 = 20.0
        QR = a3/4.*(tf**4.-ti**4.)+a2/3.*(tf**3.-ti**3.)+a1/2.*(tf**2.-ti**2.)+a0*(tf-ti)
        return QR

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
                break
        if tarifF == 0.: print("Erro no tarifário",ti,i); quit()
        return tarifF

    # Dados gerais
    g = 9.81; densidade = 1000.0
    hmin =  2.0; hmax = 7.0; hFixo = 100.0
    AF = 155.0; V0 = 620.0; hF0 = 4.0; deltahF = 0.
    LPR = 3500; LRF = 6000
    f =  0.02; d =  0.3
    # Dados da bomba
    a1 = 280.; a2 = -0.0027; etaP = 0.75
    # variáveis constantes
    f32gpi2d5 = 32.0*f/(g*math.pi**2.0*d**5.)
    aRes = (a2*3600.**2.) - f32gpi2d5*LPR - f32gpi2d5*LRF

    # Inicialização dos vetores
    timeInc = []
    CustoT = 0
    for i in range(0, nInc):
        # definição dos incrementos de tempo
        timeInc.append(empty_timeIncrem.copy())
        timeInc[i]['number'] = i + 1
        if i == 0:
            timeInc[i]['startTime'] = 0
            hF = hF0
            timeInc[i]['hFini'] = hF
            y.append(hF)
        else:
            timeInc[i]['startTime'] = timeInc[i-1]['endTime']
            timeInc[i]['hFini'] = timeInc[i-1]['hFfin']
        timeInc[i]['duration'] = 24 / nInc
        timeInc[i]['endTime'] = timeInc[i]['startTime']+timeInc[i]['duration'];
        #print ("timeInc", timeInc[i]['number'],timeInc[i]['startTime'],timeInc[i]['duration'])
        #
        # Cálculo dos volumes bombeados no incremento i
        QVC = Caudal_VC(timeInc[i]['startTime'], timeInc[i]['endTime'])
        QR = Caudal_R(timeInc[i]['startTime'], timeInc[i]['endTime']); QRmed= QR/timeInc[i]['duration']
        #
        # Ciclo iterativo de convergência (com tolerãncia=1.E-5)
        iter = 1; hFini = hF; hFmed = hF; deltahFold = 0.; tol = 1.E-6; maxIter = 8
        bRes = 2.*f32gpi2d5*LRF*QRmed/3600.
        while iter < maxIter:
            cRes = a1-hFixo -f32gpi2d5*LRF*(QRmed/3600)**2 - hFmed
            Qp = (-bRes - math.sqrt(bRes**2 - 4 * aRes * cRes))/(2*aRes) * 3600
            deltahFn = (Qp*x[i]*timeInc[i]['duration']-QVC-QR)/AF
            hF = hFini + deltahFn
            hFmed = hFini + deltahFn / 2
            #print("iter=",iter,cRes, Qp, deltahFn,deltahFold, hF, deltahFn-deltahFold)
            if math.fabs(deltahFn-deltahFold) > tol:
                deltahFold = deltahFn
            else:
                break
            iter += 1
        timeInc[i]['hFfin']= hF
        y.append(hF)
        consumo.append(QVC+QR)
        #
        # Cálculo da energia utilizada
        WP = g*densidade/etaP*Qp/3600*(a1+a2*Qp**2.)    # in W
        tarifInc = tarifario(timeInc[i]['startTime'])*timeInc[i]['duration']/1000. # in Euro/W
        Custo =  x[i]*WP*tarifInc
        CustoT += Custo
        fObjRest['g1'].append(hmin - hF); fObjRest['g2'].append(hF - hmax);
        #print("it.= %2i, x= %5.3f, hF= %6.3f, WP= %7.3f, Tarif= %5.3f, Custo= %6.3f, %7.3f, constr= %7.3f, %7.3f, <0 ?"
        #      % (i, x[i], hF, WP, tarifario(timeInc[i]['startTime']), Custo, CustoT, fObjRest['g1'][i],fObjRest['g2'][i]))

        # Cálculo de sensibilidades (aproximadas, pois consideram que Qp é independente de x)
        Sensibil['dCdx'].append(WP*tarifInc);
        dgP=Qp*timeInc[i]['duration']/(AF + 0.5*x[i]*timeInc[i]['duration']*(bRes**2-4.*aRes*cRes)**(-0.5))
        #
        # ciclo para cada dg1dx[i][j], onde i=alfa do x; j=inc. e j>=alfa
        for j in range (i, nInc): Sensibil['dg1dx'][i][j]=-dgP; Sensibil['dg2dx'][i][j]=dgP;
    # Guardar valores em Arrays
    fObjRest['fObj']=CustoT;

    # Construção da solução grafica
    #iChart = 0
    if iChart == 1:
        x1=[];y1=[];z1=[]
        for i in range(0,nInc):
            x1.insert(i,timeInc[i]['startTime']);
            y1.insert(i,timeInc[i]['hFini']);
            z1.insert(i,10*tarifario(i/(nInc/24)));
        x1.insert(nInc,timeInc[nInc-1]['endTime']); y1.insert(nInc,timeInc[nInc-1]['hFfin']); z1.insert(nInc,10*tarifario(i/(nInc/24)));
        plt.plot(x1,y1,x1[0:nInc],x[0:nInc],x1,z1);
        plt.title('Solução Proposta, Custo=%f' % CustoT); plt.xlabel('Tempo (h)');
        plt.ylabel('Nivel/ status da bomba / Tarifario (x10)'); plt.grid();
        plt.show()

    #print ("end benchmark 2018")
    return fObjRest,consumo,y;


def optimalPump(x,nInc):
    

    fObjRest, Sensibil,y = Prediction(x,1)

    def fun_obj(x):
        res, sens,y = Prediction(x,0)
        cost = res['fObj']
        return cost

    def fun_constr_1(x):
        res, sens,y = Prediction(x,0)
        g1 = res['g1']
        return g1

    def fun_constr_2(x):
        res, sens,y = Prediction(x,0)
        g2 = res['g2']
        return g2

    c1 = NonlinearConstraint(fun_constr_1, -9999999, 0, jac='2-point', hess=BFGS(), keep_feasible=False)
    c2 = NonlinearConstraint(fun_constr_2, -9999999, 0, jac='2-point', hess=BFGS(), keep_feasible=False)
    bounds = Bounds([0 for i in range(nInc)], [1 for i in range(nInc)], keep_feasible=False)
    res = minimize(fun_obj, x, args=(), method='trust-constr', jac='2-point', hess=BFGS(), constraints=[c1, c2],
               options={'verbose': 3}, bounds=bounds)
#print("res=",res)
    print("Solução final: x=",[round(res.x[i], 3) for i in range(len(res.x))])
#a=input('')

    fObjRest, Sensibil,yopt = Prediction(res.x,1)
    print("CustoF=",fObjRest['fObj'], '\n')
    cost=fObjRest['fObj']
    xopt=res.x
    
    return xopt,yopt,xopt,yopt,cost

