import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from flask import Flask, render_template, flash, request, session
from wtforms import Form, IntegerField, TextField, SelectField, SubmitField

from wtforms import validators, ValidationError
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'wk3 key'

class StartForm(Form):
    equityAlloc = IntegerField('Current Equity Allocation:')#, [validators.Required()] )
    bondAlloc = IntegerField('Current Bond Allocation:')#, [validators.Required()] )
    riskTol = SelectField('Risk Tolerance')
#    startQuarter = TextField('Initial Time:')#, [validators.Required()])#
#    endQuarter = TextField('End Time:')#, [validators.Required()])
    submit = SubmitField("Optimize")

class SecondForm(Form):
    startQuarter = SelectField('Start Quarter')
    endQuarter = SelectField('End Quarter')
    submit = SubmitField('Back Test')

def bounds_from_risk_tol(risk_tol):
    if(risk_tol==1):
        return([.20, .35, .55, .65])
    elif(risk_tol==2):
        return([.30, .45, .45, .55])
    elif(risk_tol==3):
        return([.40, .55, .35, .45])
    elif(risk_tol==4):
        return([.50, .65, .25, .35])
    elif(risk_tol==5):
        return([.60, .75, .15, .25])

def port_tsdf(portfolio, opt_portfolio, returnsDF, startQuarter, endQuarter):
    returns_small = returnsDF[(returnsDF['Quarter']>=startQuarter) & (returnsDF['Quarter']<=endQuarter)].copy()
    returns_small['Current Portfolio'] = returns_small['Equities']*portfolio['stock weight'].values[0]+returns_small['Bonds']*portfolio['bond weight'].values[0]
    returns_small['Optimal Portfolio'] = returns_small['Equities']*opt_portfolio['stock weight'].values[0]+returns_small['Bonds']*opt_portfolio['bond weight'].values[0]+returns_small['Real Estate']*opt_portfolio['real estate weight'].values[0]
    returns_small['Current'] = (returns_small['Current Portfolio'].apply(lambda x: 1+x/100).cumprod()-1)*100
    returns_small['RealAllocator'] = (returns_small['Optimal Portfolio'].apply(lambda x: 1+x/100).cumprod()-1)*100

    return(returns_small[['Quarter', 'Current Portfolio', 'Optimal Portfolio', 'Current', 'RealAllocator']])

def get_optimal_portfolio(risk_tolerance):
    #read datasets
    vp = pd.read_csv('static/vp-sharpe-all.csv')

    bds = bounds_from_risk_tol(risk_tolerance)
    vp_red = vp[((vp['stock weight']<bds[1])& (vp['stock weight']>bds[0])& (vp['bond weight']<bds[3]) & (vp['bond weight']>bds[2]))]
    opt = vp_red[vp_red['Sharpe']==vp_red['Sharpe'].max()]
    opt_df = pd.DataFrame({'name': 'RealAllocator', 'stock weight': opt['stock weight'].max(), 'bond weight': opt['bond weight'].max(), 'real estate weight': opt['real estate weight'].min(), 'Sharpe': opt['Sharpe'].mean()}, index=[0])

    return(opt_df)

@app.route('/')
def start():
    form = StartForm()
    return render_template('index.html', form = form)

@app.route('/optimized', methods = ['POST'])
def optimizer():
    form_data = request.form
    ret_df = pd.read_csv('static/asset-returns-full-quarterly-risk-free.csv')
    vp = pd.read_csv('static/vp-sharpe-all.csv')

    sw = int(form_data['equityAlloc'])/100
    #int(form_data['bondAlloc'])/100
    current_portfolio = pd.DataFrame({'name':'Current', 'stock weight':sw , 'bond weight':np.round(1-sw, decimals=2) , 'real estate weight':0}, index=[0])
    similar_port = vp[((vp['stock weight']==current_portfolio['stock weight'].max()) & (vp['bond weight']==current_portfolio['bond weight'].max()))]
    current_portfolio['Sharpe']=similar_port['Sharpe'].values[0]


    risk_tolerance = int(form_data['riskTol'])

    #optimal_portfolio = get_optimal_portfolio(current_portfolio, risk_tolerance)
    opt_portfolio = get_optimal_portfolio(risk_tolerance)
    #portfolio_comparison_df = compare_portfolios(current_portfolio, optimal_portfolio)
    port_ret1 = port_tsdf(current_portfolio, opt_portfolio, ret_df, '2018Q1', '2019Q1')
    port_ret1['Length'] = '1 Year'
    port_ret5 = port_tsdf(current_portfolio, opt_portfolio, ret_df, '2014Q1', '2019Q1')
    port_ret5['Length'] = '5 Years'
    port_ret7 = port_tsdf(current_portfolio, opt_portfolio, ret_df, '2012Q1', '2019Q1')
    port_ret7['Length'] = '7 Years'
    port_ret10 = port_tsdf(current_portfolio, opt_portfolio, ret_df, '2009Q1', '2019Q1')
    port_ret10['Length'] = '10 Years'
    port_rets = [port_ret1, port_ret5, port_ret7, port_ret10]
    port_ret_df = pd.concat(port_rets)
    opt_ahead = []
    mean_diff = []
    std_diff = []
    tr_diff = []
    for pr in port_rets:
        opt_ahead.append(pr[pr['Optimal Portfolio']>=pr['Current Portfolio']]['Quarter'].count())r
        mean_diff.append(np.round((pr['Optimal Portfolio']-pr['Current Portfolio']).mean(), decimals=3))
        std_diff.append(np.round((pr['Optimal Portfolio'].std()-pr['Current Portfolio'].std()), decimals=3))
        tr_diff.append(np.round(((1+pr['Optimal Portfolio']/100).prod()-(1+pr['Current Portfolio']/100).prod())*100, decimals=1))
    bt_results = pd.DataFrame({'Length':pd.Series([1,5,7,10]), 'opt_up':np.round(opt_ahead, decimals=0), 'mean_error':mean_diff, 'risk':std_diff, 'sum':tr_diff})

    graph5 = 'backtest5-'+str(time.time())+'.png'
    port_ret_long = pd.melt(port_ret5, id_vars=['Quarter', 'Length'], value_vars=['Current', 'RealAllocator'])
    grid = sns.lineplot(x='Quarter', y='value', data=port_ret_long, hue='variable')
    grid.set_title('5 year Back Test Total Returns') # can also get the figure from plt.gcf()
    grid.set_ylabel('Cumulative Return (%)')
    plt.setp(grid.get_xticklabels(), rotation=45, visible=True, ha='right')
    qtrs = ['2014\n Q1', '2015\n Q1', '2016\n Q1', '2017\n Q1', '2018\n Q1', '2019\n Q1']
    grid.set(xticklabels=[qtrs[i//4] if(i%4==0) else ' ' for i in range(0,4*len(qtrs))])
    plt.tight_layout()
    plt.savefig('static/'+graph5)
    plt.close()

    graph7 = 'backtest7-'+str(time.time())+'.png'
    port_ret_long = pd.melt(port_ret7, id_vars=['Quarter', 'Length'], value_vars=['Current', 'RealAllocator'])
    grid = sns.lineplot(x='Quarter', y='value', data=port_ret_long, hue='variable')
    grid.set_title('7 year Back Test Total Returns') # can also get the figure from plt.gcf()
    grid.set_ylabel('Cumulative Return (%)')
    plt.setp(grid.get_xticklabels(), rotation=45, visible=True, ha='right')
    qtrs = ['2012\n Q1', '2013\n Q1', '2014\n Q1', '2015\n Q1', '2016\n Q1', '2017\n Q1', '2018\n Q1', '2019\n Q1']
    grid.set(xticklabels=[qtrs[i//4] if(i%4==0) else ' ' for i in range(0,4*len(qtrs))])
    plt.tight_layout()
    plt.savefig('static/'+graph7)
    plt.close()

    graph10 = 'backtest10-'+str(time.time())+'.png'
    port_ret_long = pd.melt(port_ret10, id_vars=['Quarter', 'Length'], value_vars=['Current', 'RealAllocator'])
    grid = sns.lineplot(x='Quarter', y='value', data=port_ret_long, hue='variable')
    grid.set_title('10 year Back Test Total Returns') # can also get the figure from plt.gcf()
    grid.set_ylabel('Cumulative Return (%)')
    plt.setp(grid.get_xticklabels(), rotation=45, visible=True, ha='right')
    qtrs = ['2009\n Q1', '2010\n Q1', '2011\n Q1', '2012\n Q1', '2013\n Q1', '2014\n Q1', '2015\n Q1', '2016\n Q1', '2017\n Q1', '2018\n Q1', '2019\n Q1']
    grid.set(xticklabels=[qtrs[i//4] if(i%4==0) else ' ' for i in range(0,4*len(qtrs))])
    plt.tight_layout()
    plt.savefig('static/'+graph10)
    plt.close()

    session['curr_stock'] = current_portfolio['stock weight'].values[0]
    session['curr_bond'] = current_portfolio['bond weight'].values[0]
    session['curr_sharpe'] = current_portfolio['Sharpe'].values[0]

    session['opt_stock'] = opt_portfolio['stock weight'].values[0]
    session['opt_bond'] = opt_portfolio['bond weight'].values[0]
    session['opt_re'] = opt_portfolio['real estate weight'].values[0]
    session['opt_sharpe'] = opt_portfolio['Sharpe'].values[0]

    second_form = SecondForm()

    return render_template('optimized-lbt-cust.html', second_form=second_form, Quarters = ret_df['Quarter'], portfolios=current_portfolio.append(opt_portfolio), backtest5=graph5, backtest7=graph7, backtest10=graph10 , results=bt_results)

@app.route('/optCustom', methods=['POST'])
def optCustomBT():
    curr_port = pd.DataFrame({'name': 'Current', 'stock weight':session.get('curr_stock'), 'bond weight':session.get('curr_bond'), 'real estate weight': 0, 'Sharpe':session.get('curr_sharpe')}, index=[0])
    opt_port = pd.DataFrame({'name': 'RealAllocator', 'stock weight':session.get('opt_stock'), 'bond weight':session.get('opt_bond'), 'real estate weight': session.get('opt_re'), 'Sharpe':session.get('opt_sharpe')}, index=[0])

    form_data = request.form
    ret_df = pd.read_csv('static/asset-returns-full-quarterly-risk-free.csv')

    pr = port_tsdf(curr_port, opt_port, ret_df, form_data['startQ'], form_data['endQ'])

    opt_ahead = []
    mean_diff = []
    std_diff = []
    tr_diff = []
    opt_ahead.append(pr[pr['Optimal Portfolio']>=pr['Current Portfolio']]['Quarter'].count())
    mean_diff.append(np.round((pr['Optimal Portfolio']-pr['Current Portfolio']).mean(), decimals=3))
    std_diff.append(np.round((pr['Optimal Portfolio'].std()-pr['Current Portfolio'].std()), decimals=3))
    tr_diff.append(np.round(((1+pr['Optimal Portfolio']/100).prod()-(1+pr['Current Portfolio']/100).prod())*100, decimals=1))
    bt_results = pd.DataFrame({'Length':'Custom', 'opt_up':opt_ahead, 'mean_error':mean_diff, 'risk':std_diff, 'sum':tr_diff})

    graph = 'custom-backtest'+str(time.time())+'.png'
    port_ret_long = pd.melt(pr, id_vars=['Quarter'], value_vars=['Current', 'RealAllocator'])
    grid = sns.lineplot(x='Quarter', y='value', data=port_ret_long, hue='variable')
    grid.set_title('Custom Back Test Total Returns') # can also get the figure from plt.gcf()
    grid.set_ylabel('Cumulative Return (%)')
    plt.setp(grid.get_xticklabels(), rotation=45, visible=True, ha='right')
    qtrs = list(pr['Quarter'])
    grid.set(xticklabels=[qtrs[i//4] if(i%4==0) else ' ' for i in range(0,4*len(qtrs))])
    plt.tight_layout()
    plt.savefig('static/'+graph)
    plt.close()

    return render_template('backtest-cust.html', portfolios=curr_port.append(opt_port), backtest=graph , results=bt_results)


if __name__ == '__main__':
    app.run(debug=True)
