import numpy as np
import pandas as pd
import statsmodels.api as sm
import date_functions as dtf


# helper functions, the following functions are used in the ReturnSeries and ReturnFrame classes
# ===========================================================================

def _duplicates(collection):
    # Returns all duplicate variables in a collection (list, series, etc.) as a set
    freqDict = dict()
    duplicatesCollection = []
    for el in collection:
        freqDict[el] = freqDict.get(el, 0) + 1
        if freqDict[el] > 1:
            duplicatesCollection.append(el)
    return set(duplicatesCollection)


def _is_empty(collection):
    # https://www.quora.com/What-is-the-Pythonic-way-to-check-for-an-empty-set
    if not collection:
        return True
    return False


def _period_returns(_self, freq='M'):
    return _self.resample(freq).apply(lambda x: _chainlink(x))


# _chainlink function 3 to 4 times faster than pandas.Series.compound
def _chainlink(returns):
    r_compounded = 1
    for r in returns:
        r_compounded *= r + 1
    return r_compounded - 1


# ===========================================================================


class ReturnSeries(pd.Series):
    """"main functions: period_returns(freq),
                        annualize(years, monthEndDate),
                        sharpe_annualized( rf_rate, years, monthEndDate)"""

    @property
    def _constructor(self):
        return ReturnSeries

    @property
    def _constructor_expanddim(self):
        return ReturnFrame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.empty:
            assert isinstance(self.index, pd.DatetimeIndex), "ReturnSeries.index is not a pd.DateTimeIndex"

    def period_returns(self, freq='M'):
        # returns DataFrame with compounded returns per period freq. Typical freq input: 'M','Q','Y'
        return _period_returns(self, freq)

    def annualize(self, years, monthEndDate='lastMonthEnd'):
        """"Annualizes return  over a period going back # years from monthEndDate
        Args:
            years(int):period history in years which will be used for annualizing
            monthEndDate(pd.Timestamp, str): default "lastMonthEnd" selects the last day month end business day in the
            data. Dates can be given in strings as "yyyy-mm-dd" data will select month end of month in date string same
             as for Timestamps.
        Returns:
            tuple( return, sigma): returns a tuple with the annualized return and standard deviation respectively
            """
        end = dtf.get_month_end(self, monthEndDate)
        start = dtf.relative_start(end, years)
        period = self[start:end]
        r_annualized = (_chainlink(period) + 1) ** (251 / len(period)) - 1
        sigma_annualized = period.std() * (251 ** (0.5))
        return (r_annualized, sigma_annualized)  # period removed from the return

    def sharpe_annualized(self, rf_rate=0, years=1, monthEndDate='lastMonthEnd'):
        """"Returns sharpe ratio"
        Args:
            years(int, float): history period in years
            rf_rate(float, ReturnSeries): yearly risk free rate
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
        Returns:
            sharpe ratio(float)"""

        r_ann, sigma_ann = self.annualize(years, monthEndDate)
        if isinstance(rf_rate, ReturnSeries):
            rf_rate = rf_rate.annualize(years, monthEndDate)[0]
        return (r_ann - rf_rate) / sigma_ann

    def info_ratio_annualized(self, benchmark, years, monthEndDate='lastMonthEnd'):
        """"Returns information ratio
        Args:
            years(int, float): history period in years
            benchmark(ReturnSeries): benchmark
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
        Returns:
            information ratio (float)"""

        assert isinstance(benchmark, ReturnSeries)
        r_ann = self.annualize(years, monthEndDate)[0]
        r_ann_benchmark = benchmark.annualize(years, monthEndDate)[0]
        r_ann_excess, sigma_ann_excess = (self - benchmark).annualize(years, monthEndDate)
        return (r_ann - r_ann_benchmark) / sigma_ann_excess

    def tracking_error_annualized(self, benchmark, years, monthEndDate='lastMonthEnd'):
        """"Returns tracking error
        Args:
            years(int, float): history period in years
            benchmark(ReturnSeries): benchmark
            monthEndDate(pd.Timestamp, str): str format "yyyy-mm-dd
        Returns:
            Tracking error (float)"""
        return (self - benchmark).annualize(years, monthEndDate)[1]

    def regression(self, X, years, monthEndDate='lastMonthEnd'):
        """"OLS regression the ReturnSeries self is the dependent variable
        Args:
            X(ReturnFrame, ReturnSeries): independent variables in ReturnFrame for 1 or more variables, ReturnSeries for 1
            monthEndDate(str, pd.TimeStamp): str format 'yyyy-mm-dd'
            years(int): sets start date 1st day of the month # years from end date
        Returns:
            tuple(params(DataFrame), r squared(float)): params contains coefficients, tvalues, pvalues"""

        # set start and end date
        end = dtf.get_month_end(self, monthEndDate)
        start = dtf.relative_start(end, years)

        # prepare variable arrays
        y = self[start:end]
        if isinstance(X, ReturnSeries):
            X = ReturnFrame(X.loc[start:end]).copy()
        elif isinstance(X, ReturnFrame):
            X = X.loc[start:end, :].copy()
        X['Alpha'] = 1  # add intercept (see statmodels docs)

        # fit model and prepare parameter Dataframe to return
        model = sm.OLS(y, X)
        result = model.fit()
        params = pd.concat([result.params, result.tvalues, result.pvalues], axis=1).rename(
            columns={0: "params", 1: "tvalues", 2: "pvalues"})
        return params, result.rsquared

    def ytd_return(self, monthEndDate='lastMonthEnd'):
        end = dtf.get_month_end(self, monthEndDate)
        start = end - pd.offsets.BYearBegin(n=1)
        return _chainlink(self[start:end])

    def month_return(self, monthEndDate='lastMonthEnd'):
        end = dtf.get_month_end(self, monthEndDate)
        start = end - pd.offsets.BMonthBegin(n=1)
        return _chainlink(self[start:end])

    def compounded_return(self, monthStartDate, monthEndDate='lastMonthEnd'):
        # returns a  single compounded return over period monthStartDate to monthEndDate
        end = dtf.get_month_end(self, monthEndDate)
        start = dtf.ts_date(monthStartDate) - pd.offsets.BMonthBegin(n=0)
        return _chainlink(self[start:end])

    def compounded_series(self, monthStartDate, monthEndDate='lastMonthEnd'):
        # returns a compounded return series starting from monthStartDate till monthEndDate
        end = dtf.get_month_end(self, monthEndDate)
        start = dtf.ts_date(monthStartDate) - pd.offsets.BMonthBegin(n=0)
        period = self[start:end]
        compoundedSrs = pd.Series(index=period.index)
        for i in range(len(period)):
            if i == 0:
                compoundedSrs.iloc[i] = period.iloc[0]
            else:
                compoundedSrs.iloc[i] = (compoundedSrs.iloc[i - 1] + 1) * (period.iloc[i] + 1) - 1
        return compoundedSrs


class ReturnFrame(pd.DataFrame):

    @property
    def _constructor(self):
        return ReturnFrame

    @property
    def _constructor_sliced(self):
        return ReturnSeries

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.empty:
            assert isinstance(self.index,
                              pd.DatetimeIndex), "DataFrame index is not a DateTimeIndex"

        # assert that dataframe has no duplicate column names as this will prohibit underlying Series to be transformed
        #  to ReturnSeries
        assert _is_empty(_duplicates(self.columns)), "DataFrame has the following duplicate column names: " + str(
            _duplicates(self.columns))

    def period_returns(self, freq='M'):
        return _period_returns(self, freq)

    def regression(self, y, X, years, monthEndDate='lastMonthEnd'):
        """"OLS regression
        Args:
            y(str): dependent variable
            X(str, list): independent variables
            years(int, float): years before month end date to determine start
            monthEndDate(str, pd.TimeStamp): month end date. Format 'yyyy-mm-dd'
        Returns:
            tuple(params(DataFrame), r squared(float)): params contains coefficients, tvalues, pvalues
            """
        return self.loc[:, y].regression(self.loc[:, X], years, monthEndDate)

    def coltypes(self):
        # checks of what type columns are (i.e. pd.Series or pd.ReturnSeries)
        for col in self.columns:
            print(str(col) + '\t\t : ' + str(type(self[col])))

    # The following summary functions will loop stats for multiple years and return them as dataframe
    # Will be replaced by summary functions on the ReturnSeries level and then wrapped into functions on
    #  the ReturnFrame level
    # ===========================================================================
    def annualized_summary(self, fund, yearsList, columns=("return", "sigma"), monthEndDate='lastMonthEnd'):
        results = []
        index = []
        for year in yearsList:
            results.append(self[fund].annualize(year, monthEndDate))
            index.append(str(year) + ' year')
        return pd.DataFrame(results, columns=columns, index=index)

    def sharpe_summary(self, fund, rf_rate, yearsList, monthEndDate='lastMonthEnd'):
        results = []
        index = []
        for year in yearsList:
            if isinstance(rf_rate, str):
                results.append(self[fund].sharpe_annualized(self[rf_rate], year, monthEndDate))
            else:
                results.append(self[fund].sharpe_annualized(rf_rate, year, monthEndDate))
            index.append(str(year) + ' year')
        return pd.DataFrame(results, columns=["SR"], index=index)

    def info_summary(self, fund, benchmark, yearsList, monthEndDate='lastMonthEnd'):
        results = []
        index = []
        for year in yearsList:
            results.append(self[fund].info_ratio_annualized(self[benchmark], year, monthEndDate))
            index.append(str(year) + ' year')
        return pd.DataFrame(results, columns=["IR"], index=index)

    # combines all summary functions into a report/list
    def summary_fund(self, fund, benchmark, betas, rf_rate=0, yearsList=[1, 3, 5], monthEndDate='lastMonthEnd'):
        ann = self.annualized_summary(fund, yearsList, monthEndDate=monthEndDate)
        ann_bm = self.annualized_summary(benchmark, yearsList, columns=['r_bm', 's_bm'], monthEndDate=monthEndDate)
        sr = self.sharpe_summary(fund, rf_rate, yearsList, monthEndDate)
        ir = self.info_summary(fund, benchmark, yearsList, monthEndDate)
        reg = self.regression(fund, betas, max(yearsList))
        summary = pd.concat([ann, ann_bm, sr, ir], axis=1)
        print(summary)
        print()
        print(reg)
        return


def coltypes(df):
    for col in df.columns:
        print(str(col) + '\t\t : ' + str(type(df[col])))
