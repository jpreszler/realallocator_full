#port-sim-w-rf-ret-out.py

#This file has the bulk of useful code for the later app.

#It reads the NPI data and aggregates to remove property type and MSA grouping.
#The aggregated data is merged with market index data and ultimately written to
#the main return data file: 'asset-returns-quarterly-risk-free.csv'
#This data file was then hand edited to fill in missing bond returns since 2015
#using iShares GOVT returns. This most closely match the Barclays data which no
#longer exists.

#This is a general problem, especially for bonds, most major
#index based ETF's have changed name or structure since 1978. The government
#bonds which have lower returns had the most stability in naming so they were
#used for the initial version of the product. Coprporate bonds seemed to have
#higher returns and more volatility, making them better competition for Equities
#but the problem of putting all allocation (or as much as allowed) into real
#estate would still happen.

#Besides this data generation, this file contains that original versions of the
#code that built a dataframe of returns over time and draw the efficient frontier
#clouds in the MVP. The dataframe of returns over time was used for backtest
#results in the app. The efficient frontier over a set time interval was abandoned
#once the Bayesian posterior sampling was working since both the efficient frontier
#and Sharpe ratio (which are essentially the same information) are highly dependent
#on the return results. Additionally, the method of incorporating risk tolerance here
#is based on quantiles over the range of observed risk as opposed to set bounds
#on asset weights. The quantile approach leads to unrealistic optimal portfolios
#such as no bonds, almost all real estate, and varying additions of equities
#based on risk. This can re-create the equity-bond splits commonly used, but
#when adding real estate, bonds are essentially abandoned and a 2 asset portfolio
# is developed with equities and real estate.

#This file is based used as a notebook.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data_path = '/home/jpreszler/github/insight-project/data/'
dl_path = '/home/jpreszler/Downloads/'

#npi_full = pd.read_excel(dl_path+'NPI Annualized Detail_20191.xlsx')
msa = pd.read_excel(dl_path+'NPI Annualized MSA_20191.xlsx')
mi = pd.read_excel(data_path+'market-indices_20191.xlsx')

#reshape market index info
mi_wide = mi.pivot_table(index='Quarter', columns = 'Index', values = 'Return', fill_value = 0)

#re-organize msa data and aggregate down to quarter
ret_by_msa = msa.groupby(['msa', 'yyq']).TotalReturn.agg(['count', 'mean', 'std', 'min', 'max'])
ret_by_msa = ret_by_msa.reset_index(level=-2).reset_index(level=-1)
mean_totalreturns = ret_by_msa.groupby('yyq')['mean'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index(level=-1)
mean_totalreturns['Quarter'] = mean_totalreturns['yyq'].apply(lambda x: str(x)[:4]+'Q'+str(x)[4:])

#join market index with RE returns
returns = mi_wide.join(mean_totalreturns.set_index('Quarter')['mean'])
returns = returns.rename(columns = {'mean':'RE mean'})
returns.columns
returns_small = returns[['S&P 500 Index', 'T-Bills (90 day)', 'Barclays Capital Govt Bond', 'RE mean']]

returns_small.apply(np.mean, axis=0)

#get portfolios from the output of mk-portfolio-all.py instead of this.
wts = np.linspace(start=0,stop=1,num=100,endpoint=True).round(decimals=2)
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
portfolios.head()
portfolios.shape

#compute risk and return of a portfolio over last 40 years.
portfolios['return'] = portfolios['stock weight']*returns_small['S&P 500 Index'].mean()+portfolios['bond weight']*returns_small['Barclays Capital Govt Bond'].mean()+portfolios['real estate weight']*returns_small['RE mean'].mean()

portfolios['risk'] = (portfolios['stock weight']*returns_small['S&P 500 Index'].std())**2+(portfolios['bond weight']*returns_small['Barclays Capital Govt Bond'].std())**2+(portfolios['real estate weight']*returns_small['RE mean'].std())**2+2*portfolios['stock weight']*portfolios['bond weight']*returns_small['S&P 500 Index'].cov(returns_small['Barclays Capital Govt Bond'])+2*portfolios['stock weight']*portfolios['real estate weight']*returns_small['S&P 500 Index'].cov(returns_small['RE mean'])+2*portfolios['bond weight']*portfolios['real estate weight']*returns_small['Barclays Capital Govt Bond'].cov(returns_small['RE mean'])

portfolios['return'].describe()
portfolios['risk'] = np.sqrt(portfolios['risk']).round(decimals=3)
portfolios['risk'].describe()
sns.scatterplot(x='risk', y='return', hue='Max Wt Category', data=portfolios)
last_plot = sns.scatterplot(x='risk', y='return', hue='Max Wt Category', data=portfolios)
last_plot.get_figure().savefig('/home/jpreszler/github/insight-project/total_frontier.png')

maxrr = portfolios.groupby('risk')['return'].agg(['max']).reset_index(level=-1)
maxrr.describe()

##stock and bond only - looking into 2 asset allocations
bond_wts = 1- stock_wts
cols2 = ['stock weight', 'bond weight']
portfolios2 = pd.DataFrame(columns = cols2)
for sw in stock_wts:
    for bw in bond_wts:
        if(sw+bw==1):
            portfolios2 = portfolios2.append(pd.Series([sw,bw], index=cols2), ignore_index=True)
portfolios2.head()

portfolios2['return'] = portfolios2['stock weight']*returns_small['S&P 500 Index'].mean()+portfolios2['bond weight']*returns_small['Barclays Capital Govt Bond'].mean()

portfolios2['risk'] = (portfolios2['stock weight']*returns_small['S&P 500 Index'].std())**2+(portfolios2['bond weight']*returns_small['Barclays Capital Govt Bond'].std())**2+2*portfolios2['stock weight']*portfolios2['bond weight']*returns_small['S&P 500 Index'].cov(returns_small['Barclays Capital Govt Bond'])

portfolios2['return'].describe()
portfolios2['risk'] = np.sqrt(portfolios2['risk'])
portfolios2['risk'].describe()
sns.scatterplot(x='risk', y='return', data=portfolios2)
portfolios2.head()

#2 asset quantile approach
p2quants = portfolios2['risk'].quantile([.2,.4,.6,.8])
p2quants.values

growth_band = portfolios2[(portfolios2['risk']>=p2quants[0.4]) & (portfolios2['risk']<=p2quants[0.6])].copy()
max_in_growth = growth_band['return'].max()
p2g_opt = portfolios2[portfolios2['return']==max_in_growth]
p2g_opt

#COmputes portfolios risk and return over a set of asset return data.
def portrr_df(returnDF, startQuarter, endQuarter):
    #load portfolios
    rr_df = pd.read_csv('/home/jpreszler/github/insight-project/data/3d-portfolios.csv')
    #select return subset
    returns_small = returnDF[(returnDF['Quarter']>=startQuarter) & (returnDF['Quarter']<=endQuarter)]

    #compute portfolio return
    rr_df['return'] = rr_df['stock weight']*returns_small['Equities'].mean()+rr_df['bond weight']*returns_small['Bonds'].mean()+rr_df['real estate weight']*returns_small['Real Estate'].mean()

    #compute risk for portfolio
    rr_df['risk'] = (rr_df['stock weight']*returns_small['Equities'].std())**2+(rr_df['bond weight']*returns_small['Bonds'].std())**2+(rr_df['real estate weight']*returns_small['Real Estate'].std())**2+2*rr_df['stock weight']*rr_df['bond weight']*returns_small['Equities'].cov(returns_small['Bonds'])+2*rr_df['stock weight']*rr_df['real estate weight']*returns_small['Equities'].cov(returns_small['Real Estate'])+2*rr_df['bond weight']*rr_df['real estate weight']*returns_small['Bonds'].cov(returns_small['Real Estate'])
    rr_df['risk'] = np.sqrt(rr_df['risk']).round(decimals=4)

    return(rr_df)

#here we rename columns and save to the main return datafile.
ret2 = returns_small.rename(columns = {'S&P 500 Index':'Equities', 'Barclays Capital Govt Bond':'Bonds', 'RE mean':'Real Estate', 'T-Bills (90 day)':'Risk Free'}).reset_index(level=-1)

ret2.head()
ret2.to_csv('/home/jpreszler/github/insight-project/asset-returns-quarterly-risk-free.csv', index=False)

#Exploring quantile approach and impact of time on efficient frontier.
ret3 = ret2.set_index('Quarter')
ret3.apply(np.mean, axis=0).values
ret3.apply(np.count_nonzero, axis=0)
first = portrr_df(ret2, '1978Q1', '1988Q4')
second = portrr_df(ret2, '1989Q1', '1999Q4')
third = portrr_df(ret2, '2000Q1', '2010Q4')
fourth = portrr_df(ret2, '2011Q1', '2019Q1')

first['Time'] = '1'
second['Time'] = '2'
third['Time'] = '3'
fourth['Time'] = '4'
timerr = pd.concat([first, second, third, fourth])
g = sns.FacetGrid(timerr, col='Time', hue='Max Wt Category')
g = g.map(plt.scatter, 'risk', 'return').add_legend()

timerr.groupby('Time')['risk'].describe()

sns.distplot(timerr['risk'], kde=True, rug=True)

sns.distplot(first['risk'], kde=True, rug=True)
sns.distplot(second['risk'], kde=True, rug=True)
sns.distplot(third['risk'], kde=True, rug=True)
sns.distplot(fourth['risk'], kde=True, rug=True)

quants = first['risk'].quantile([.2,.4,.6,.8])
quants2 = first['risk'].quantile([0,.2,.4,.6,.8,1])
list(quants2)
quants[0.2]
type(list(quants))
len(list(quants))

#function to draw cloud of all porfolios risk v return so efficient frontier can be seen.
#quantile boundaries are drawn in black
def draw_port_cloud(port_df, color='Max Wt Category'):
    eff_cloud = sns.scatterplot(x='risk', y='return', hue=color, data=port_df)
    quantiles = port_df['risk'].quantile([.2,.4,.6,.8])
    max_ret = port_df['return'].max()
    eff_cloud.axvline(x=quantiles[0.2], ymin=0,ymax=max_ret, c='black')
    eff_cloud.axvline(x=quantiles[0.4], ymin=0,ymax=max_ret, c='black')
    eff_cloud.axvline(x=quantiles[0.6], ymin=0,ymax=max_ret, c='black')
    eff_cloud.axvline(x=quantiles[0.8], ymin=0,ymax=max_ret, c='black')
    plt.show()

draw_port_cloud(first)
draw_port_cloud(second)
draw_port_cloud(third)
draw_port_cloud(fourth)


#the function to obtain optimal portfolio via the quantile approach.
def get_opt_port(port_df, lower_risk, upper_risk):
    risk_band = port_df[(port_df['risk']>=lower_risk) & (port_df['risk']<=upper_risk)]
    max_return_in_band = risk_band['return'].max()
    return(risk_band[risk_band['return']==max_return_in_band])

growth = get_opt_port(first, quants[0.6], quants[0.8])

growth

#variations on portrr_df that allow returns over time for a portfolio (or 2 portfolios) to be visualized.
def port_tsdf(portfolio, returnsDF, startQuarter, endQuarter):
    returns_small = returnsDF[(returnsDF['Quarter']>=startQuarter) & (returnsDF['Quarter']<=endQuarter)].copy()
    returns_small['Portfolio'] = returns_small['Equities']*portfolio['stock weight'].values+returns_small['Bonds']*portfolio['bond weight'].values+returns_small['Real Estate']*portfolio['real estate weight'].values
    return(returns_small)

def port_tsdf2(portfolio, opt_portfolio, returnsDF, startQuarter, endQuarter):
    returns_small = returnsDF[(returnsDF['Quarter']>=startQuarter) & (returnsDF['Quarter']<=endQuarter)].copy()
    returns_small['Current Portfolio'] = returns_small['Equities']*portfolio['stock weight'].values+returns_small['Bonds']*portfolio['bond weight'].values
    returns_small['Optimal Portfolio'] = returns_small['Equities']*opt_portfolio['stock weight'].values+returns_small['Bonds']*opt_portfolio['bond weight'].values+returns_small['Real Estate']*opt_portfolio['real estate weight'].values
    return(returns_small[['Current Portfolio', 'Optimal Portfolio']])


#some exploration
first_g_opt = port_tsdf(growth, ret2, '2000Q1', '2019Q1')
first_g_opt.head()

sns.lineplot(x='Quarter', y='value', hue='variable', data=pd.melt(first_g_opt, id_vars=['Quarter'], value_vars = ['Equities', 'Bonds', 'Real Estate', 'Portfolio']))

crash = portrr_df(ret2, '2007Q2', '2009Q3')
crash_risk_quant = crash['risk'].quantile([.2,.4,.6,.8])
crash_opt_g = get_opt_port(crash, crash_risk_quant[.6],crash_risk_quant[.8])
crash_opt_ts = port_tsdf(crash_opt_g, ret2, '2009Q4', '2019Q1')

def draw_future_perform(port_ts_df):
    sns.lineplot(x='Quarter', y='value', hue='variable', data=pd.melt(port_ts_df, id_vars=['Quarter'], value_vars = ['Equities', 'Bonds', 'Real Estate', 'Portfolio']))

draw_future_perform(crash_opt_ts)

test = portrr_df(ret2, '2011Q1', '2013Q4')
testQuants = list(test['risk'].quantile([0,.2,.4,.6,.8,1]))
test_opt = get_opt_port(test, testQuants[1], testQuants[2])

test_opt
