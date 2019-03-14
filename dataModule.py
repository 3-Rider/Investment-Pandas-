import pandas as pd
import returnClasses as rc
import date_functions as dtf

""""module to convert prices into returns and load the data in an DataFrame, index is set to a DateTimeIndex. 
The columns contain fund/index returns"""


def csv_to_df(file, dateformat='%d/%m/%Y'):
    # Converts csv to DataFrame, sets index to dates
    # first column in csv file has to contain dates
    df = pd.read_csv(file)
    df = df.set_index(df.columns[0])  # sets first column as index
    df.index = pd.to_datetime(df.index, format=dateformat, errors='coerce').normalize()
    return pd.DataFrame(df)


# load csv files into data frames
# ==============================================================


def get_data():
    folder = 'data\\'

    # specify fund and benchmark files
    fundCsv = folder + 'JANIX_fund.csv'
    benchmarkCsv = folder + '^RUO_bm.csv'
    ffCsv = folder + 'F-F_Research_Data_Factors_daily.CSV'

    # make sure dateformat below is consistent with files
    fundDf = csv_to_df(fundCsv, dateformat='%Y-%m-%d')
    benchmarkDf = csv_to_df(benchmarkCsv, dateformat='%Y-%m-%d')
    ffDf = csv_to_df(ffCsv, dateformat='%Y%m%d').divide(100)

    # create price DataFrame
    df = pd.DataFrame(fundDf['Adj Close']).rename(columns={'Adj Close': 'Fund'})
    df = df.join(benchmarkDf['Adj Close'], how='outer').rename(columns={'Adj Close': 'BM'})
    df = df['2010-02':].dropna()

    # create return DataFrame
    df = df.pct_change()
    df = df.join(ffDf, how='outer')
    df = df['2010-03':].dropna()
    df = rc.ReturnFrame(df)  # convert DataFrame to ReturnFrame
    return df


if __name__ == '__main__':
    rdf = get_data()
    print('min date in dataset: {}'.format(rdf.index.min()))
    print('max date in dataset: {}'.format(rdf.index.max()))
    print()
    print(rdf.head())

    # print(rdf.resample('Y').count())
