from rich.live import Live
from rich.table import Table
import redis
import pandas as pd
import yfinance

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
                row[i] = f"[green]+{value:3.2f}%" if float(value) >= 0 else f"[red]{value:3.2f}%"
            if "SGD=X" in columns[i]:
                row[i] = f"{value:3.4f}"
            
        except ValueError:
            continue
        
def get_past_fx( date_str ):
    end = libs.utils.add_to_date(date_str=date_str)
    df = yfinance.ticker.Ticker("SGD=X").history(start=date_str, end=end)
    return df[['Open', 'High', 'Low', 'Close']].mean(axis=1).values[0]

class PnlRunner:
    
    def __init__(self):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe("marketdata")
        self.market_prices = {}
        
    def generate_table(self) -> Table:
        """Make a new table."""
        bookdf = pd.read_csv(f"{CONFIG_DIR_PATH}/book_saxo.csv")
        bookdf['open_date']     = bookdf['open_date'].apply( libs.utils.dateformat )
        bookdf['_SGD=X']        = bookdf['open_date'].apply( get_past_fx )
        bookdf['SGD=X']         = self.market_prices.get("SGD=X")
        bookdf['cost_value']    = bookdf['cost_price'].astype(float) * bookdf['qty']
        bookdf['price']         = bookdf['symbol'].map( self.market_prices )
        bookdf['mtm_value']     = bookdf['price'].astype(float) * bookdf['qty']
        bookdf['mtm_value_sgd'] = bookdf['mtm_value'].astype(float) * bookdf['SGD=X'].astype(float)
        bookdf['pnl']           = bookdf['mtm_value'] - bookdf['cost_value']
        bookdf['returns']       = 100 * (( bookdf['price'].astype(float) / bookdf['cost_price'].astype(float) ) - 1)
        bookdf['pnl_sgd']       = bookdf['pnl'] * bookdf['SGD=X'].astype(float)
        bookdf['returns_fx']        = 100 * (( bookdf['SGD=X'].astype(float) / bookdf['_SGD=X'].astype(float) ) - 1)
        
        bookdf.fillna("-", inplace=True)
        
        table = Table()
        for column in bookdf.columns:
            table.add_column( column )
        
        for rows in bookdf.astype(str).values:
            style_values(rows, bookdf.columns)
            table.add_row( *rows )
        
        return table

    def run(self):
        with Live(self.generate_table(), refresh_per_second=1) as live:
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message['data'].decode('utf-8')
                    if data:
                        pairs = data.strip(":").split(":")
                        data = {key: value for key, value in (pair.split("=", 1) for pair in pairs)}
                        self.market_prices.update({ data['identifier']: data['price'] })
                        live.update(self.generate_table())

def main():
    pnlRunner = PnlRunner()
    pnlRunner.run()
    
    
