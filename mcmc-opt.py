#Attempt to built MCMC optimization approach to explore the portfolio space.

#Works, but gives similar result to more deterministic approach and multiple
#MCMC runs seem to get stuck in a infinite loop trying to pick new_port.

#Also, runs much slower than simply grabbing max sharpe.
import numpy as np
import pandas as pd


portfolios = pd.read_csv('/home/jpreszler/github/insight-project/data/vp-sharpe-all.csv')
returns = pd.read_csv('/home/jpreszler/github/insight-project/asset-returns-full-quarterly-risk-free.csv')

def get_next_portfolio(current_portfolio, riskTol):
    sw_current = current_portfolio['stock weight'].values
    bw_current = current_portfolio['bond weight'].values
    rew_current = current_portfolio['real estate weight'].values
    initial_sharpe = current_portfolio['Sharpe'].values

    new_port = pd.DataFrame(columns = current_portfolio.columns)

    while(new_port.shape[0]==0):
    #select equity and bond decrease
        np.random.seed()
        eq_dec = np.random.choice(range(0, riskTol+3))/100
        bond_dec = np.random.choice(range(0, 8-(riskTol+1)))/100
        new_eq = sw_current-eq_dec
        new_bond = bw_current-bond_dec
        new_re = rew_current+eq_dec+bond_dec

        new_port = portfolios[((portfolios['stock weight']==new_eq[0]) & (portfolios['bond weight']==new_bond[0]))]# & (portfolios['real estate weight']==new_re[0]))]

    if((new_port['Sharpe'].mean() - initial_sharpe) <= 0):
        return(current_portfolio)
    elif((new_port['Sharpe'].mean() - initial_sharpe) > .05):
        return(new_port)
    elif((new_port['Sharpe'].mean() - initial_sharpe)<= .05):
        pick = np.random.binomial(1, (new_port['Sharpe'].mean() - initial_sharpe)/.05)
        if(pick==1):
            return(current_portfolio)
        else:
            return(new_port)


def get_optimal_end(current_portfolio, riskTol):
    initial_rew = current_portfolio['real estate weight'].values
    initial_sharpe = current_portfolio['Sharpe'].values
    fail = False
    old_count = 0
    next_port = current_portfolio

    while(not fail):
        next_port = get_next_portfolio(next_port, riskTol)
        if(next_port['real estate weight'].mean() == current_portfolio['real estate weight'].mean()):
            result = 'old'
        else:
            result = 'new'
        if(result == 'old'):
            old_count += 1
        if((old_count > 15) or ((next_port['real estate weight'].values - initial_rew) > .25)):
            fail = True

    return(next_port)
