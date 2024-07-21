import re
import mplfinance as fplt
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore")

def _match_regex(cols, cols_regex, to_set=False):
    result = []
    for col in cols:
        for regex in cols_regex:
            matched = re.match(regex, col)
            if matched:
                result.append( col )
                
    if to_set:
        result = set( result )
        
    return result

def plot_graph(df, start=None, end=None, selected_cols_regex=None, panel_cols_regex=None):
    default_cols = {'open', 'high', 'low', 'close', 'volume', 'split_ratio', 'dividend', 'capital_gains'}
    
    selected_cols_regex = set(selected_cols_regex) if selected_cols_regex else set()
    panel_cols_regex    = set(panel_cols_regex) if panel_cols_regex else set()
    if type(panel_cols_regex) == str:
        panel_cols_regex = set([ panel_cols_regex ])
    
    extra_cols = set(df.columns) - default_cols
    extra_cols = _match_regex(extra_cols, selected_cols_regex.union(panel_cols_regex), to_set=True)
    panel_cols = _match_regex(extra_cols, panel_cols_regex, to_set=True)
    
    _df = df[start: end]
    
    add_plots = []
    panel_count = 2 # starts at 2 because of default ohlc chart + volume panels
    for extra_col in extra_cols:
        if extra_col in panel_cols:
            add_plots.append( fplt.make_addplot(_df[ extra_col ], type='line', secondary_y=True, panel=panel_count) )
            panel_count += 1
        else:
            add_plots.append( fplt.make_addplot(_df[ extra_col ]) )
        
    height = 10 + len(panel_cols_regex)
    fplt.plot(_df, type='candle', style = 'yahoo',
          addplot = add_plots,
          volume=True, figsize=(21, height))
    
    
def add_to_date(date_str, delta=None):
    # {'days: 365}
    delta = delta or {'days': 365}
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    new_date = date_obj + timedelta(**delta)
    new_date_str = new_date.strftime('%Y-%m-%d')
    return new_date_str