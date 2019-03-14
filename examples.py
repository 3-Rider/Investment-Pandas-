import dataModule
import returnClasses as rc
import date_functions as dtf

fund = 'Fund'  # string
benchmark = 'BM'  # string
rf_rate = 'RF'
date = 'lastMonthEnd'

# below creates a ReturnFrame with data
rdf = dataModule.get_data()

print('rdf data type: {}'.format(type(rdf)))
print()
print(rdf.head())
print()

# accessing a ReturnSeries
rsrsF = rdf.loc[:, fund]
print('rsrs data type: {}'.format(type(rsrsF)))
print()
print(rsrsF.head())
print()

rsrsBM = rdf.loc[:, benchmark]
rsrsRF = rdf.loc[:, rf_rate]

# functions that use years and monthEndDate use the 2 functions below from date_functions.py
endDate = dtf.get_month_end(rsrsF, date=date)
startDate = dtf.relative_start(endDate, years=3)
print('The sample for the 3 year statistics start at {} and ends on {} \n'.format(startDate, endDate))

# calculate stats based on a ReturnSeries in the ReturnFrame
annualized_return_3Y, annualized_standard_dev_3Y = rsrsF.annualize(years=3, monthEndDate=date)

print('The annualized return and standard deviation based on the last 3 years are:'
      '\n Return: {:.2%} \n Standard Deviation: {:.2%}'.format(annualized_return_3Y, annualized_standard_dev_3Y))
print('\n Without formatting numbers: \n {} , {}'.format(annualized_return_3Y, annualized_standard_dev_3Y))
print()

# calculate sharpe ratio
sharpe_ratio_3Y = rsrsF.sharpe_annualized(rf_rate=rsrsRF, years=3, monthEndDate=date)
print('The sharpe ratio based on the last 3 years is: {:.2f}'.format(sharpe_ratio_3Y))

# calculate information ratio
information_ratio_3Y = rsrsF.info_ratio_annualized(benchmark=rsrsBM, years=3, monthEndDate=date)

print('The information ratio based on the last 3 years is: {:.2f}'.format(information_ratio_3Y))

# calculate information ratio
TE_3Y = rsrsF.tracking_error_annualized(benchmark=rsrsBM, years=3, monthEndDate=date)

print('The TE based on the last 3 years is: {:.2f}'.format(TE_3Y))
print()

# example of aggregating returns per quarter. Also works on returnSeries
Q_returns = rdf.period_returns(freq='Q')
print('Quarterly returns for quarters ending on index date')
print(Q_returns.head())
