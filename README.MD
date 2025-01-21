### TODO
- save df to csv locally
- ML modelling on marked sides
- feature analysis
- yearly split backtesting

### IDEAS
- C++ (code something + multithreading)
- monte carlo Mar 2010 - Dec 2015
- enhance side marker (candle + indicators plot)
- trading gym environment
- portfolio/strategy tracker


https://query1.finance.yahoo.com/v7/finance/download/TQQQ?period1=1682998941&period2=1714621341&interval=1d&events=history&includeAdjustedClose=true

https://github.com/stefan-jansen/machine-learning-for-trading


```
    LOWER = MID - std * stdev
    UPPER = MID + std * stdev

    BANDWIDTH = 100 * (UPPER - LOWER) / MID
    PERCENT = (close - LOWER) / (UPPER - LOWER)
```


https://neptune.ai/blog/anomaly-detection-in-time-series


identifier=VOO:price=550.0:time=1737161999000:exchange=PCX:quoteType=QuoteType.ETF:marketState=MarketState.POST:changePercent=0.09827429801225662:change=0.53997802734375:priceHint=2