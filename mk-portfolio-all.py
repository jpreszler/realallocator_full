#mk-portfolio-all.py

#Creates all combinations of 3 class portfolios satisfying:
#   1) all weights >=.01 (or 1%)
#   2) sum of weights is 1 (or 100%)
#   3) Smallest change is .01 (or 1%)

#Also determines which class has the most allocation and saves data to file.
#Output path should be changed before execution.


import numpy as np
import pandas as pd

wts = np.linspace(start=0.01,stop=1,num=100,endpoint=True).round(decimals=2)
stock_wts = wts
bond_wts = wts
re_wts = wts
cols = ['stock weight', 'bond weight', 'real estate weight', 'Max Wt Category']
portfolios = pd.DataFrame(columns = cols)
for sw in stock_wts:
    for bw in bond_wts:
        for rw in re_wts:
            if(sw+bw+rw==1):
                if(sw>=bw):
                    if(sw>=rw):
                        mw = 'stock'
                    else:
                        mw = 'real estate'
                else:
                    if(bw>=rw):
                        mw = 'bond'
                    else:
                        mw = 'real estate'
                portfolios = portfolios.append(pd.Series([sw,bw,rw, mw], index=cols), ignore_index=True)

portfolios.to_csv('/home/jpreszler/github/insight-project/data/3d-portfolios-nz.csv', index=False)
