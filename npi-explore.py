#npi-explore.py

#Code to explore and process the original NPI data.
#This is intended to be run in notebook style (done with atom/hydrogen).
#most useful code here exists elsewhere, this is initial exploration of the NPI data.



import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pymc3

print('Running on NumPy v{}'.format(np.__version__))
print('Running on Pandas v{}'.format(pd.__version__))
print('Running on MatPlotLib v{}'.format(mpl.__version__))
print('Running on Seaborn v{}'.format(sns.__version__))
print('Running on PyMC3 v{}'.format(pymc3.__version__))

data_path = '/home/jpreszler/github/insight-project/data/'
dl_path = '/home/jpreszler/Downloads/'

npi_full = pd.read_excel(dl_path+'NPI Annualized Detail_20191.xlsx')
msa = pd.read_excel(dl_path+'NPI Annualized MSA_20191.xlsx')
mi = pd.read_excel(data_path+'market-indices_20191.xlsx')

mi.head()

sns.lineplot(x='Quarter', y='Return', hue='Index', data=mi, legend=False)

mi.groupby('Index').agg(['count', 'mean', 'std', 'min', 'max'])

sns.lineplot(x='Quarter', y='Return', hue='Index', data=mi.loc[mi.Index.isin(['NPI', 'S&P 500 Index', 'Consumer Price Index'])])

#reshape mi for covariance calc
mi_wide = mi.pivot_table(index='Quarter', columns = 'Index', values = 'Return', fill_value = 0)

mi_wide.corr()

sns.heatmap(mi_wide.corr())

msa.head()

ret_by_msa = msa.groupby(['msa', 'yyq']).TotalReturn.agg(['count', 'mean', 'std', 'min', 'max'])
ret_by_msa = ret_by_msa.reset_index(level=-2).reset_index(level=-1)
mean_totalreturns = ret_by_msa.groupby('yyq')['mean'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index(level=-1)
mean_totalreturns.head()
sns.lineplot(x='yyq', y='mean', data=mean_totalreturns, legend = False)

mean_totalreturns['Quarter'] = mean_totalreturns['yyq'].apply(lambda x: str(x)[:4]+'Q'+str(x)[4:])
mean_totalreturns.head()
df = pd.melt(mean_totalreturns, id_vars = ['yyq', 'Quarter', 'count'], value_vars = ['mean', 'std'])
df.head()
sns.lineplot(x='Quarter', y='value', hue='variable', data=df)

mean_totalreturns['MRQA'] = mean_totalreturns['mean'].rolling(4).mean()
mean_totalreturns['MRQSD'] = mean_totalreturns['mean'].rolling(4).std()

mi_wide.info()

returns = mi_wide.join(mean_totalreturns.set_index('Quarter')['mean'])

returns = returns.rename(columns = {'mean':'RE mean'})

sns.heatmap(returns.corr())

returns.describe()

returns = returns.reset_index(level=-1)
sns.lineplot(x='Quarter', y='value', hue='variable', data = pd.melt(returns, id_vars = ['Quarter'], value_vars = ['NAREIT Equity REIT Index', 'S&P 500 Index','RE mean']))
