import yfinance
import itertools
import pandas as pd

class IncrementalCorrelationFactory:
    
    def __init__(self, symbols):
        self.pairs = list( itertools.combinations(symbols, 2) )
        
        df = pd.DataFrame()
        for symbol in symbols:
            _df = yfinance.ticker.Ticker( symbol ).history(period="1d", interval="1m")['Close']
            _df.name = symbol
            df = pd.concat([df, _df], axis=1)
            
        df.ffill(inplace=True)
        
        for symbol in symbols:
            df[f'{symbol}_norm'] = (df[symbol] - df[symbol].mean()) / df[symbol].std()
            
        df[[ f'{symbol}_norm' for symbol in symbols ]].plot()
        
        
        
if __name__ == "__main__":
    icf = IncrementalCorrelationFactory(symbols=['VOO', 'ARKF'])