#mk-portfolio-risk-valid.py

#Constructs dataset of valid portfolios based on equity and bond bounds for
#risk tolerences. Saves dataset to file.
#Can be run as script or notebook.

#Ultimately not used in final app.

import numpy as np
import pandas as pd

def equity_bond_bounds_from_risk_tol(tolerance):
    '''Returns list of the form [equity min, equity max, bond min, bond max]'''
    if(tolerance==1):
        return([.1,.3,.7,1])
    elif(tolerance==2):
        return([.2,.4, .6,1])
    elif(tolerance==3):
        return([.3,.5, .3, .5])
    elif(tolerance==4):
        return([.6,1, .2,.4])
    elif(tolerance==5):
        return([.7,1,.1, .3])

emin, emax, bmin, bmax = equity_bond_bounds_from_risk_tol(1)
wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = np.linspace(start=emin, stop=emax, num=int((emax-emin)*100)).round(decimals=2)
bond_wts = np.linspace(start=bmin, stop=bmax, num=int((bmax-bmin)*100)).round(decimals=2)
cols = ['stock weight', 'bond weight', 'real estate weight', 'risk tolerance']
portfolios = pd.DataFrame(columns = cols)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw<1):
            rw = 1-(sw+bw)
            portfolios = portfolios.append(pd.Series([sw,bw,rw.round(decimals=2), 1], index=cols), ignore_index=True)

emin, emax, bmin, bmax = equity_bond_bounds_from_risk_tol(2)
wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = np.linspace(start=emin, stop=emax, num=int((emax-emin)*100)).round(decimals=2)
bond_wts = np.linspace(start=bmin, stop=bmax, num=int((bmax-bmin)*100)).round(decimals=2)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw<1):
            rw = 1-(sw+bw)
            portfolios = portfolios.append(pd.Series([sw,bw,rw.round(decimals=2), 2], index=cols), ignore_index=True)

emin, emax, bmin, bmax = equity_bond_bounds_from_risk_tol(3)
wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = np.linspace(start=emin, stop=emax, num=int((emax-emin)*100)).round(decimals=2)
bond_wts = np.linspace(start=bmin, stop=bmax, num=int((bmax-bmin)*100)).round(decimals=2)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw<1):
            rw = 1-(sw+bw)
            portfolios = portfolios.append(pd.Series([sw,bw,rw.round(decimals=2), 3], index=cols), ignore_index=True)

emin, emax, bmin, bmax = equity_bond_bounds_from_risk_tol(4)
wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = np.linspace(start=emin, stop=emax, num=int((emax-emin)*100)).round(decimals=2)
bond_wts = np.linspace(start=bmin, stop=bmax, num=int((bmax-bmin)*100)).round(decimals=2)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw<1):
            rw = 1-(sw+bw)
            portfolios = portfolios.append(pd.Series([sw,bw,rw.round(decimals=2), 4], index=cols), ignore_index=True)

emin, emax, bmin, bmax = equity_bond_bounds_from_risk_tol(5)
wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = np.linspace(start=emin, stop=emax, num=int((emax-emin)*100)).round(decimals=2)
bond_wts = np.linspace(start=bmin, stop=bmax, num=int((bmax-bmin)*100)).round(decimals=2)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw<1):
            rw = 1-(sw+bw)
            portfolios = portfolios.append(pd.Series([sw,bw,rw.round(decimals=2), 5], index=cols), ignore_index=True)

portfolios.shape
portfolios.to_csv('/home/jpreszler/github/insight-project/data/3d-portfolios-with-re-and-risk.csv', index=False)
