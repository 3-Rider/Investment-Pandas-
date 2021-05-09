This project shows how Python and Pandas (a Python package) can be used to calculate return and risk statistics in a scalable manner by expanding the pandas module. 

The project includes an example in which it creates a factsheet. The factsheet that was created by the code can be found in the "output examples" folder. This was based on the input
data in the "data" folder. The example uses the Janus Henderson Triton Fund Class D fund (JANIX) data and the Russell 2000 growth index (^RUO) data as its benchmark. 
The focus of the example is to illustrate the statistics that can be calculated with the code.

Created by Eelco Ridder

================================================

This code is build around the module returnClasses.py, which introduces the classes ReturnFrame and ReturnSeries. 
These extend the Pandas classes DataFrame and Series and are used to manipulate return information and calculate return based investment statistics. Currently the code only works with geometric returns.
All methods that work on pandas DataFrames and Series work on ReturnFrames and ReturnSeries.

The main.py module serves as an example that uses the returnClasses when you run it to create a factsheet in excel. The returnClasses could be leveraged to calculate investment statistics over a large manager database
 and make a manager ranking based on these statistics. A more basic example of the use of returnClasses can be found in examples.py

The examples use the Janus Henderson Triton Fund Class D fund (JANIX) data and the Russell 2000 growth index (^RUO) data as its benchmark. 

================= Dependencies ================= 

Python libraries:
- Numpy
- Pandas
- Openpyxl
- Matplotlib
- Seaborn
- Statsmodels

================= CREATION OF A ReturnFrame AND ReturnSeries =================

Each column of a ReturnFrame is a ReturnSeries. Both classes will have to have a DateTimeIndex as an index. Use pandas.to_datetime() function to convert a date column to a DateTimeIndex. 
The values of a ReturnSeries and ReturnFrame consist of returns where 1% is represented as 0.01. 
A pandas Series and DataFrame can be converted using them as arguments for ReturnSeries() and ReturnFrame() respectively (i.e. ReturnSeries(pandas Series))

The module dataModule shows an example on how to prepare a ReturnFrame based on multiple price files downloaded from yahoo finance
 and fama french factor portfolio returns downloaded from ( http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html )



================= returnClasses MODULE =================

The returnClasses module is dependent on some date functions on the date_functions module. The majority of the methods for calculating statistics can be accessed through the ReturnSeries. 
When working with a ReturnFrame access the ReturnSeries/column to be able to use the method (i.e. by using the loc function like returnframe.loc[:,column_name].method() )



================= Current ReturnSeries methods =================

.period_returns(freq='M')
	returns DataFrame with compounded returns per period freq. Typical freq input: 'M','Q','Y'


.annualize(years, monthEndDate='lastMonthEnd')
	Annualizes return and standard deviation over a period going back # years from monthEndDate
    	Args:
		years(int):period history in years which will be used for annualizing 
		monthEndDate(pd.Timestamp, str): default "lastMonthEnd" selects the last day month end business day in the data. 
		Dates can be given in strings as "yyyy-mm-dd" data will select month end of month in date string same as for Timestamps.
	Returns:
        	tuple( return, sigma): returns a tuple with the annualized return and standard deviation respectively

		
.sharpe_annualized(rf_rate=0, years=1, monthEndDate='lastMonthEnd'):
        Returns sharpe ratio
        Args:
            years(int, float): history period in years
            rf_rate(float, ReturnSeries): yearly risk free rate
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
        Returns: 
            sharpe ratio(float)

		
.info_ratio_annualized(benchmark,years, monthEndDate='lastMonthEnd')
	Returns information ratio
	Args:
            years(int, float): history period in years
            benchmark(ReturnSeries): benchmark
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
        Returns:
            information ratio (float)

			
.tracking_error_annualized( benchmark, years,  monthEndDate='lastMonthEnd'):
        Returns tracking error
        Args:
            years(int, float): history period in years
            benchmark(ReturnSeries): benchmark
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
	Returns:
	    Tracking error (float)

			
.regression( X, years, monthEndDate='lastMonthEnd')
	OLS regression the ReturnSeries self is the dependent variable
        Args:
            X(ReturnFrame, ReturnSeries): independent variables in ReturnFrame for 1 or more variables, ReturnSeries for 1
            monthEndDate(str, pd.TimeStamp): str format 'yyyy-mm-dd'
            years(int): sets start date 1st day of the month # years from end date
        Returns:
            tuple(params(DataFrame), r squared(float)): params contains coefficients, tvalues, pvalues

			
.ytd_return( monthEndDate = 'lastMonthEnd')
	calculates the ytd return until monthEndDate


.month_return( monthEndDate = 'lastMonthEnd')
	calculates the month return for the month of the monthEndDate


.compounded_return( monthStartDate, monthEndDate = 'lastMonthEnd')
	returns a  single compounded return over period monthStartDate to monthEndDate


.compounded_series( monthStartDate, monthEndDate = 'lastMonthEnd')
	returns a compounded return series starting from monthStartDate till monthEndDate



================= Current ReturnFrame methods =================
	
.period_returns(freq='M')
	returns DataFrame with compounded returns per period freq. Typical freq input: 'M','Q','Y'
	
.regression(y, X, years, monthEndDate='lastMonthEnd'):
	OLS regression, wrapped the ReturnSeries regression method. The difference is that y and X are input as a string and list.
	Args:
		y(str): dependent variable
		X(str, list): independent variables
		years(int, float): years before month end date to determine start
		monthEndDate(str, pd.TimeStamp): month end date. Format 'yyyy-mm-dd'
	Returns:
		tuple(params(DataFrame), r squared(float)): params contains coefficients, tvalues, pvalues
		

.coltypes()
	prints types of the columns in the ReturnFrame. These should all be ReturnSeries

	
The ReturnFrame class also contains several summary functions these still work but are depreciated and will be replaced/removed
they are:
.annualized_summary(self, fund, yearsList, columns=("return", "sigma"), monthEndDate='lastMonthEnd')
.sharpe_summary( fund, rf_rate, yearsList, monthEndDate='lastMonthEnd')
.info_summary(self, fund, benchmark, yearsList, monthEndDate='lastMonthEnd')
.summary_fund(self, fund, benchmark, betas, rf_rate=0, yearsList=[1, 3, 5], monthEndDate='lastMonthEnd')		