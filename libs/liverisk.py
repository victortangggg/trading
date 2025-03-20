from rich.live import Live
from rich.table import Table
from rich.layout import Layout
import redis
import pandas as pd
import yfinance
from functools import lru_cache

import libs.utils

CONFIG_DIR_PATH = r"C:\Users\User\Desktop\projects\trading\configs"


def style_values( row, columns ):
    for i, value in enumerate(row):
        try:
            value = float(value)
            row[i] = f"{value:3.2f}"
            if "pnl" in columns[i].lower():
                row[i] = f"[green]+{value:3.2f}" if float(value) >= 0 else f"[red]{value:3.2f}"
            if "returns" in columns[i].lower():
                row[i] = f"[green]+{value:3.2f} %" if float(value) >= 0 else f"[red]{value:3.2f} %"
            if "weight" in columns[i].lower():
                row[i] = f"{value:3.1f} %"
            if "SGD=X" in columns[i]:
                row[i] = f"{value:3.4f}"
            
        except ValueError:
            continue
        
@lru_cache
def get_past_fx( date_str ):
    end = libs.utils.add_to_date(date_str=date_str)
    yf_ticker_obj = yfinance.ticker.Ticker("SGD=X")
    df = yf_ticker_obj.history(start=date_str, end=end)
    if df.empty:
        return yf_ticker_obj.info["ask"]
    return float( df[['Open', 'High', 'Low', 'Close']].mean(axis=1).values[0] )


class LiveRiskRunner:
    
    def __init__(self, bookfile="book_saxo.csv"):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe("marketdata")
        self.market_prices = {}
        self.lowest_market_prices = {}
        self.book_file_path = f"{CONFIG_DIR_PATH}/{bookfile}"
        self.stoploss_threshold = 0.01
        
        df = pd.read_csv( self.book_file_path )
        symbols = [ symbol for symbol in list(df['symbol'].values) if symbol != "ACCOUNTCASH"]
        for symbol in symbols:
            ticker_info = yfinance.ticker.Ticker( symbol ).info
            self.market_prices[symbol] = float(ticker_info["regularMarketPreviousClose"])
            self.lowest_market_prices[symbol] = ticker_info['dayLow']
        
        
    def generate_layout(self):
        layout = Layout(name="pnl")
        layout.split_column(
            Layout(name="upper"),
            Layout(name="lower")
        )
        return layout
        
        
    def generate_table(self) -> Table:
        bookdf = pd.read_csv( self.book_file_path )
        #bookdf = bookdf.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtypes != 'object' else col)
        
        cashdf = bookdf[ bookdf['symbol'] == 'ACCOUNTCASH']
        bookdf = bookdf[ bookdf['symbol'] != 'ACCOUNTCASH']
        
        bookdf['open_date']     = bookdf['open_date'].apply( libs.utils.dateformat )
        bookdf['_SGD=X']        = bookdf['open_date'].apply( get_past_fx )
        bookdf['SGD=X']         = self.market_prices.get("SGD=X")
        bookdf['cost_value']    = bookdf['open_price'] * bookdf['qty']
        bookdf['price']         = bookdf['symbol'].map( self.market_prices )
        bookdf['mtm_value']     = bookdf['price'] * bookdf['qty']
        bookdf['mtm_value_sgd'] = bookdf['mtm_value'] * bookdf['SGD=X']
        bookdf['pnl']           = bookdf['mtm_value'] - bookdf['cost_value']
        bookdf['returns']       = 100 * (( bookdf['price'] / bookdf['open_price'] ) - 1)
        bookdf['pnl_sgd']       = bookdf['pnl'] * bookdf['SGD=X']
        bookdf['returns_fx']    = 100 * (( bookdf['SGD=X'] / bookdf['_SGD=X'] ) - 1)
        bookdf['sl']            = (1-self.stoploss_threshold) * bookdf['symbol'].map( self.lowest_market_prices ).clip(lower=bookdf['open_price'])
        
        mtm_value_sgd_total = bookdf['mtm_value_sgd'].sum()        
        if mtm_value_sgd_total:
            bookdf['weight'] = ( bookdf['mtm_value_sgd'] / mtm_value_sgd_total ) * 100
        
        bookdf.fillna("-", inplace=True)
        
        total_row_values = []
        table = Table()
        for column in bookdf.columns:
            table.add_column( column )
            if column in {"cost_value", "mtm_value", "mtm_value_sgd", "pnl", "pnl_sgd", "weight"}:
                total_row_values.append( bookdf[column].sum() )
            elif column == "returns":
                total_row_values.append( (bookdf['pnl'].sum() / bookdf['cost_value'].sum()) * 100 )
            else:
                total_row_values.append( "---" )
        
        for rows in bookdf.astype(str).values:
            style_values(rows, bookdf.columns)
            table.add_row( *rows )
            
        style_values(total_row_values, bookdf.columns)
        table.add_row( *total_row_values )
            
        cashdf['open_date']     = cashdf['open_date'].apply( libs.utils.dateformat )
        cashdf['_SGD=X']        = cashdf['open_date'].apply( get_past_fx )
        cashdf['SGD=X']         = self.market_prices.get("SGD=X")
        cashdf['USD']           = cashdf['open_price'] * cashdf['qty']
        cashdf['SGD']           = cashdf['USD'] * cashdf['SGD=X']
        cashdf['returns_fx']    = 100 * (( cashdf['SGD=X'] / cashdf['_SGD=X'] ) - 1)
        cashdf['equity+cash']   = cashdf['SGD'] + bookdf['mtm_value_sgd'].sum()
        cashdf['weight']        = (cashdf['SGD'] / cashdf['equity+cash']) * 100
        
        cashdf.fillna("-", inplace=True)
        
        cashtable = Table()
        for column in cashdf.columns:
            cashtable.add_column( column )
            
        for rows in cashdf.astype(str).values:
            style_values(rows, cashdf.columns)
            cashtable.add_row( *rows )
        
        layout = self.generate_layout()
        layout['upper'].update(table)
        layout['lower'].update(cashtable)
        return layout
    
    
    def _lowest_market_prices(self, symbol, price):
        if symbol not in self.lowest_market_prices or price < self.lowest_market_prices.get(symbol) :
            self.lowest_market_prices[ symbol ] = price


    def run(self):
        with Live(self.generate_table(), refresh_per_second=1) as live:
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message['data'].decode('utf-8')
                    if data:
                        pairs = data.strip(":").split(":")
                        data = {key: value for key, value in (pair.split("=", 1) for pair in pairs)}
                        symbol = data['identifier']
                        price = float( data['price'] )
                        self.market_prices.update({ symbol: price })
                        self._lowest_market_prices(symbol, price)
                        live.update(self.generate_table())


def main():
    liveRiskRunner = LiveRiskRunner()
    liveRiskRunner.run()
    
    
if __name__ == "__main__":
    main()