import yfinance as yf
from pandas_datareader import data as pdr
from backtesting import Backtest
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

#PLOT_EXPORT_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\backtests"
PLOT_EXPORT_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\apps\\backtests"

class BTData:
    def __init__(self, ticker, start_date=None, end_date=None, split_yearly=True) -> None:
        yfTicker = yf.Ticker(ticker)
        if not start_date:
            first_trade_timestamp = yfTicker.history_metadata.get('firstTradeDate')
        self.start_date = start_date or datetime.fromtimestamp(first_trade_timestamp)
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        if split_yearly:
            self.yearly_date_ranges = self._generate_yearly_date_ranges(self.start_date, self.end_date)
        else:
            self.yearly_date_ranges = [(self.start_date, self.end_date)]
        
        
    def _generate_yearly_date_ranges(self, start_date, end_date):
        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Initialize a list to store the yearly date ranges
        yearly_date_ranges = []
        
        # Generate yearly date ranges
        current_year_start = start_date
        while current_year_start < end_date:
            next_year_start = datetime(current_year_start.year + 1, current_year_start.month, current_year_start.day)
            if next_year_start > end_date:
                next_year_start = end_date
            yearly_date_ranges.append((current_year_start.strftime('%Y-%m-%d'), next_year_start.strftime('%Y-%m-%d')))
            current_year_start = next_year_start
        
        return yearly_date_ranges
        
    

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
        
    def _write_stats_html(self, stats, plot_filename):
        
        def _color_negative_red(val):
            return 'color: red' if type(val) == float and val < 0 else None

        key_stats = stats.filter(items=[
            'Start', 'End', 'Duration', 'Exposure Time [%]', 'Equity Final [$]',
            'Equity Peak [$]', 'Return [%]', 'Buy & Hold Return [%]',
            'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
            'Sortino Ratio', 'Calmar Ratio', 'Max. Drawdown [%]',
            'Avg. Drawdown [%]', 'Max. Drawdown Duration', 'Avg. Drawdown Duration',
            '# Trades', 'Win Rate [%]', 'Best Trade [%]', 'Worst Trade [%]',
            'Avg. Trade [%]', 'Max. Trade Duration', 'Avg. Trade Duration',
            'Profit Factor', 'Expectancy [%]', 'SQN', '_strategy'])
        
        style = """
        <style>
        .container {
            display: flex;
        }
        .left-column {
            flex: 1; /* Adjust the flex value to change the width */
            padding: 20px;
            border: 1px solid #ccc;
        }
        .right-column {
            flex: 2; /* Adjust the flex value to change the width */
            padding: 20px;
            border: 1px solid #ccc;
        }
        th, td {
            font-size: 13px;
        }
        tr {
            border: 1px solid black;
        }
        </style>
        """
        key_stats_df = key_stats.to_frame(name='values')
        html = f"""
            { style }
            <div class="container">
                <div class="left-column">
                    <h3>Key Stats</h3>
                    { 
                        key_stats_df.style.applymap(_color_negative_red).set_table_styles(
                            [
                                {"selector": "", "props": [("border", "1px solid black")]},
                                {"selector": "tbody td", "props": [("border", "1px solid black")]},
                                {"selector": "th", "props": [("border", "1px solid black")]}
                            ]
                        ).to_html()
                    }
                </div>
                <div class="right-column">
                    <h3>Trades</h3>
                    { stats.get('_trades').style.applymap(_color_negative_red).set_table_styles(
                        [
                            {"selector": "", "props": [("border", "1px solid black")]},
                            {"selector": "tbody td", "props": [("border", "1px solid black")]},
                            {"selector": "th", "props": [("border", "1px solid black")]}
                        ]
                    ).to_html() }
                </div>
            </div>
        """
        
        with open( plot_filename, 'a') as html_file:
            html_file.write( html )
    
    def run(self):
        bt = Backtest(self.data, self.strategy, commission=self.commission, exclusive_orders=True)
        stats = bt.run()
        plot_filename = f'{PLOT_EXPORT_DIR}\\{self.strategy_name}.html'
        bt.plot( filename=plot_filename, open_browser=False )
        
        self._write_stats_html(stats=stats, plot_filename=plot_filename)
            
        return stats