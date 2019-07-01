#cluster-market-cond.py

#Produces asset returns with spectral clustering labels which are then used as "market conditions"
#by other code (like 'assign-sharpe.ipynb')

#intended to be run notebook style, created with atom/hydrogen.

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
returns = pd.read_csv('/home/jpreszler/github/realallocator_full/data/asset-returns-full-quarterly-risk-free.csv')

plt.scatter(returns['Equities'], returns['Bonds'])
plt.scatter(returns['Equities'], returns['Real Estate'])
plt.scatter(returns['Real Estate'], returns['Bonds'])


from sklearn.cluster import  SpectralClustering
sc = SpectralClustering(3, affinity='nearest_neighbors', n_init=100,
                         assign_labels='discretize')
returns['SC label'] = sc.fit_predict(returns.set_index('Quarter'))
returns.groupby('SC label').describe()

returns.groupby(['SC label']).agg(['mean', 'std', 'min', 'max', 'count'])


returns.to_csv('/home/jpreszler/github/realallocator_full/data/sc-label-returns.csv', index=False)

ret_label_long = pd.melt(returns, id_vars=['SC label', 'Quarter'], value_vars = ['Equities', 'Bonds', 'Real Estate', 'Risk Free'])
lfg = sns.FacetGrid(data=ret_label_long, hue='SC label', col='variable')
lfg.map(sns.distplot, 'value', hist=False)
