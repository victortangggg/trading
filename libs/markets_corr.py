from datetime import date, datetime, timedelta
import yfinance as yf
from jinja2 import Environment, FileSystemLoader

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
        
    def run(self):
        df = yf.download( tickers=self.tickers, start=self.start_date, end=self.as_of_date)
        adj_close_df = self._standardize_ffill(df, column='Adj Close')
        corr_df = adj_close_df.corr()
        return corr_df
    
    
class MarketRunningCorr(MarketCorrBase):
    
    def __init__(self, tickers, start_date, end_date=None, window=30) -> None:
        end_date = self._today_if_none(end_date)
        
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        
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
            current_date_obj += timedelta(days=1)
            
        return result
        
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
            
        
        