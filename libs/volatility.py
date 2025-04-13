import yfinance as yf
import pandas as pd
import numpy as np

pd.options.mode.copy_on_write = True

def get_volatility( symbol, periods=None, start=None, end=None, date_format="%Y-%m-%d", col="Close"):
    if not periods:
        periods = 30
        
    if not start and not end:
        today = pd.Timestamp.today().normalize()
        business_dates = pd.date_range(end=today, periods=periods, freq='B')
        start = business_dates[0].strftime( date_format )
        end = business_dates[-1].strftime( date_format )
        
    ticker = yf.Ticker( symbol )
    df = ticker.history(start=start, end=end)
    return get_df_volatility( df, col=col )


def get_df_volatility( df, col="Close" ):
    #df['Returns'] = ( df[ col ] / df[ col ].shift() ).dropna()
    df['Returns'] = df[ col ].pct_change()
    return np.std( df['Returns'] ) * np.sqrt(252)


def populate_df_volatility( df, symbol, periods=30, date_col="Date", date_format="%Y-%m-%d", col="Close"):
    df = df.reset_index()
    start = df[ date_col ].min()
    end = df[ date_col ].max()
    business_dates = pd.date_range(end=start, periods=periods, freq='B')
    pre_start = business_dates[0]
    
    pre_df = yf.Ticker( symbol ).history(start=pre_start, end=start).reset_index()
    j = len(pre_df)
    df_total = pd.concat([pre_df, df], ignore_index=True)
    
    result = []
    while j < len(df_total):
        i = max(0, j-periods)
        volatility = get_df_volatility( df_total.iloc[i:j] )
        result.append( volatility )
        j += 1
        
    df['Volatility'] = result
    return df

    

if __name__ == "__main__":
    
    populate_df_volatility( yf.Ticker("TQQQ").history(start="2025-03-13", end="2025-04-13"), symbol="TQQQ" )