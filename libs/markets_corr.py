from datetime import date, datetime, timedelta
import yfinance as yf
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import json

DATE_FORMAT = "%Y-%m-%d"


class MarketCorrBase:
    def _today_if_none(self, date_string) -> str:
        if not date_string:
            return date.today().strftime(DATE_FORMAT)
        return date_string
        
    def _standardize_ffill(self, df, column='Adj Close'):
        standardized_df = ( df[column] - df[column].mean() ) / df[column].std()
        standardized_df.fillna(method='ffill', inplace=True)
        return standardized_df
    
    def _defaultdict_to_dict(self, d):
        if isinstance(d, defaultdict):
            d = {k: self._defaultdict_to_dict(v) for k, v in d.items()}
        return d


class MarketCorr(MarketCorrBase):
    
    def __init__(self, tickers, start_date=None, as_of_date=None, lookback=30) -> None:
        
        as_of_date = self._today_if_none(as_of_date)
            
        if not start_date:
            as_of_date_obj = datetime.strptime(as_of_date, DATE_FORMAT)
            start_date_obj = as_of_date_obj - timedelta(days=lookback)
            start_date = start_date_obj.strftime(DATE_FORMAT)
            
        self.tickers = tickers
        self.start_date = start_date
        self.as_of_date = as_of_date
        self.result = None
        
    def run(self):
        df = yf.download( tickers=self.tickers, start=self.start_date, end=self.as_of_date)
        adj_close_df = self._standardize_ffill(df, column='Adj Close')
        corr_df = adj_close_df.corr()
        self.result = corr_df
        
    def get(self):
        return self.result
    
    
class MarketRunningCorr(MarketCorrBase):
    
    def __init__(self, tickers, start_date, end_date=None, window=30, interval=1) -> None:
        end_date = self._today_if_none(end_date)
        
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        self.interval = interval
        self._result = None
        self.result = None
        self.corr_changes = None
        self.changes_pct = None
        
    def run(self):
        start_date_obj = datetime.strptime(self.start_date, DATE_FORMAT)
        end_date_obj = datetime.strptime(self.end_date, DATE_FORMAT)
        current_date_obj = start_date_obj
        result = {}
        while current_date_obj <= end_date_obj:
            current_start_date_obj = current_date_obj - timedelta(days=self.window)
            start = current_start_date_obj.strftime(DATE_FORMAT)
            end = current_date_obj.strftime(DATE_FORMAT)
            df = yf.download(tickers=self.tickers, start=start, end=end)
            cleaned_df = self._standardize_ffill(df, column='Adj Close')
            result[end] = cleaned_df.corr()
            current_date_obj += timedelta(days=self.interval)
            
        # last_df = cleaned_df.tail(2)
        # changes_pct_df = ( last_df / last_df.shift(1) ) - 1
        # changes_pct = changes_pct_df.dropna().to_dict("records")[0]
        
        last_df = df.fillna(method='ffill').tail(2)['Adj Close']
        changes_pct_df = ( ( last_df / last_df.shift(1) ) - 1 ) * 100
        changes_pct = changes_pct_df.dropna().to_dict("records")[0]
        
        self.changes_pct = changes_pct
        self._result = result
        
    def _process_t_1(self):
        corr_changes = defaultdict( lambda: defaultdict( float ) )
        for ticker_a, corr in self.result.items():
            for ticker_b, values in corr.items():
                change = values[-1] - values[-2]
                corr_changes[ ticker_a ][ ticker_b ] = change
                
        self.corr_changes = self._defaultdict_to_dict( corr_changes )
        
    def _process_result(self):
        result = defaultdict( lambda: defaultdict( list ) )
        for date_key, corr_df in self._result.items():
            corr_data = corr_df.to_json()
            corr_dict = json.loads( corr_data )
            for ticker_a, ticker_b_data in corr_dict.items():
                for ticker_b, corr_value in ticker_b_data.items():
                    result[ ticker_a ][ ticker_b ].append( corr_value )
            
        self.result = self._defaultdict_to_dict( result )
        
    def get(self):
        self._process_result()
        self._process_t_1()
        return self.result, self.corr_changes, self.changes_pct
    
        
class HTMLTemplate:
    
    TEMPLATE_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\libs\\templates\\"
    OUTPUT_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\apps\\"
    
    def __init__(self, **kwargs) -> None:
        self.context = kwargs
        
    def render(self):
        environment = Environment(loader=FileSystemLoader(self.TEMPLATE_DIR))
        with open(self.OUTPUT_DIR + "markets_corr.html", mode="w", encoding="utf-8") as out:
            template = environment.get_template("markets_corr.template")
            out.write( template.render(self.context) )





### TEST ###

# MACRO_TICKERS = [
#     'SHY', 
#     'VXX', 
#     'EWS', 
#     'TQQQ', 
#     'GSG', 
#     'UJB', 
#     'TYD', 
#     'GLD',
#     'BTC-USD',
#     'SGD=X',
# ]

# SECTORS_TICKERS = [
#     'XLY',
#     'XLP',
#     'XLE',
#     'XLF',
#     'XLV',
#     'XLI',
#     'XLB',
#     'XLK',
#     'XLU',
#     'XME',
#     'GDX',
#     'IYR',
#     'XHB',
#     'XRT',
# ]

# DATE_FORMAT = '%Y-%m-%d'
# LOOKBACK = 30

# today = date.today()
# start_date_t0 = ( today - timedelta(days=LOOKBACK) ).strftime(DATE_FORMAT)

# macros_running_corr = MarketRunningCorr(tickers=MACRO_TICKERS, start_date=start_date_t0)
# macros_running_corr.run()
# macro_corr_data_t0, macro_corr_changes, macro_changes = macros_running_corr.get()

# sectors_running_corr = MarketRunningCorr(tickers=SECTORS_TICKERS, start_date=start_date_t0)
# sectors_running_corr.run()
# sectors_corr_data_t0, sectors_corr_changes, sector_changes = sectors_running_corr.get()