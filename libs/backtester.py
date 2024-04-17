import yfinance as yf
from pandas_datareader import data as pdr
from backtesting import Backtest
import warnings
warnings.filterwarnings("ignore")

PLOT_EXPORT_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\backtests"

class Backtester:
    def __init__(self, strategy, data, capital=10000.0, commission=0.0) -> None:
        self.strategy = strategy
        
        try:
            self.strategy_name = strategy.NAME.replace(' ', '_')
        except:
            raise ValueError("Please indicate name in your Strategy class")
        
        self.data = data
        self.capital = capital
        self.commission = commission
    
    def run(self):
        bt = Backtest(self.data, self.strategy, commission=self.commission, exclusive_orders=True)
        stats = bt.run()
        plot_filename = f'{PLOT_EXPORT_DIR}\\{self.strategy_name}.html'
        bt.plot( filename=plot_filename, open_browser=False )
        print(stats)