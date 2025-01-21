import re
import mplfinance as fplt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

import warnings
warnings.filterwarnings("ignore")

DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d"]

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
    
def convert_to_dateobj(date_str):
    for date_format in DATE_FORMATS:
        try:
            dateobj = datetime.strptime(date_str, date_format)
            return dateobj
        except ValueError:
            continue
        
    # Raise an error if no formats match
    raise ValueError(f"Date string '{date_str}' is not in a recognized format.")
    
def dateformat(date_str):
    if not date_str or isinstance(date_str, float):
        current_year = datetime.now().year
        dateobj = datetime(current_year, 1, 1)
    else:
        dateobj = convert_to_dateobj(date_str=date_str)
    return dateobj.strftime('%Y-%m-%d')
    
def add_to_date(date_str, delta=None):
    # {'days: 365}
    delta = delta or {'days': 365}
    date_obj = convert_to_dateobj(date_str=date_str) #datetime.strptime(date_str, '%Y-%m-%d')
    new_date = date_obj + timedelta(**delta)
    new_date_str = new_date.strftime('%Y-%m-%d')
    return new_date_str


def split_df(df, window=30, step=1):
    subdfs = [ df.iloc[i: i+window] for i in range(0, len(df), step) ]
    return subdfs


def plot_scatter_line_comp( dfscatter, dfline, dfline_cols = None ):
    
    dfscatter_cols = dfscatter.columns
    if len(dfscatter_cols) != 2:
        raise ValueError("dfscatter needs to have exactly 2 fields")
    
    if not dfline_cols:
        dfline_cols = dfline.columns

    # Scatter plot for columns A and B
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))  # Creating subplots for scatter and line plot
    scatter = ax[0].scatter(dfscatter[ dfscatter_cols[0] ], dfscatter[ dfscatter_cols[1] ], picker=True)  # Scatter plot with picking enabled
    ax[0].set_title(f'Scatter Plot ({dfscatter_cols[0]} vs {dfscatter_cols[1]})')
    ax[0].set_xlabel(dfscatter_cols[0])
    ax[0].set_ylabel(dfscatter_cols[1])

    # Define what happens when a point is selected
    def onpick(event):
        ind = event.ind  # Get index of the selected point
        selected_row = dfline.iloc[ind[0]]  # Retrieve the row data based on index
        print(f'Selected row:\n{selected_row}')
        
        # Clear previous line plot
        ax[1].clear()

        # Plotting the line graph for the selected row
        ax[1].plot(dfline_cols, selected_row.values, marker='o')
        ax[1].set_title(f'Line Plot for row {ind[0]}')
        ax[1].set_xlabel('Columns')
        ax[1].set_ylabel('Values')

        # Redraw the figure to update it
        fig.canvas.draw()

    # Connect the scatter plot with the event handler
    fig.canvas.mpl_connect('pick_event', onpick)

    plt.show()