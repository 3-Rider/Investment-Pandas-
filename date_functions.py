import numpy as np
import pandas as pd


# set end date
def ts_date(date):
    # converts date (in format yyyy-m-dd) to normalized pd.TimeStamp date (normalized)
    if isinstance(date, pd.Timestamp):
        date = date.normalize()
    elif isinstance(date, str):
        date = pd.to_datetime(date, format='%Y-%m-%d').normalize()
    else:
        raise TypeError
    return date


# set start date
def relative_start(date, years):
    # returns business month start # years relative to date
    date = ts_date(date)
    start = date - pd.offsets.BMonthBegin(n=years * 12)
    return start


def get_month_end(rsrs, date='lastMonthEnd'):
    """" returns month end date of given month in date if it's in the rsrs.index date range else it will return
     last month end in the rsrs.index. Default returns the last month date in the data.
    Args:
        rsrs(ReturnSeries):
        date(str): 'dd/mm/yyyy'"""

    if date == 'lastMonthEnd':
        monthEnd = _last_month_end_in_rsrs(rsrs)  # Business month end of rsrs.index.max date

    else:
        monthEnd = ts_date(date) - pd.offsets.BMonthEnd(n=0)  # Business month end of date
        if not _date_in_daterange(monthEnd, rsrs):
            monthEnd = _last_month_end_in_rsrs(rsrs)

    # print("month end date: " + str(monthEnd))
    return monthEnd


# Helper Functions
# ==========================================================================


def _last_month_end_in_rsrs(rsrs):
    monthEnd = rsrs.index.max().normalize() - pd.offsets.BMonthEnd(n=0)  # Business month end of rsrs.index.max date
    if not _date_in_daterange(monthEnd, rsrs):  # True when month end is not in rsrs.index date range
        monthEnd = rsrs.index.max().normalize() - pd.offsets.BMonthEnd(n=1)  # previous month end
    return monthEnd


def _date_in_daterange(date, rsrs):
    if rsrs.index.min().normalize() <= date <= rsrs.index.max().normalize():
        return True
    else:
        return False


# test case
if __name__ == '__main__':
    start = '2018-01-01'
    end = '2018-06-25'

    index = pd.bdate_range(start, end)
    srs = pd.Series(range(len(index)), index=index)

    print(get_month_end(srs))
    print(get_month_end(srs, '2017-01-01'))
    print(get_month_end(srs, '2019-01-01'))
    print(get_month_end(srs, '2018-04-01'))
    print(get_month_end(srs, '2018-06-30'))
