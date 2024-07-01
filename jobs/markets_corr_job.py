from libs.markets_corr import MarketRunningCorr, HTMLTemplate
from datetime import date, timedelta
import os

TICKERS = [
    'SHY', 
    'VXX', 
    'EWS', 
    'TQQQ', 
    'GSG', 
    'UJB', 
    'TYD', 
    'GLD',
    'BTC-USD',
    'SGD=X'
]

DATE_FORMAT = '%Y-%m-%d'
LOOKBACK = 30
APP_HTML_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\apps\\"
ARCHIVE_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\archive\\markets_corr\\"

today = date.today()
start_date = ( today - timedelta(days=LOOKBACK) ).strftime(DATE_FORMAT)

past_html_path = APP_HTML_DIR + "markets_corr.html"
archive_path = ARCHIVE_DIR + f"markets_corr.{today.strftime(DATE_FORMAT)}.html"
if os.path.exists( past_html_path ) and not os.path.exists( archive_path ):
    os.rename( past_html_path, archive_path)

market_running_corr = MarketRunningCorr(tickers=TICKERS, start_date=start_date)
market_running_corr.run()
corr_data = market_running_corr.get()

htmlTemplate = HTMLTemplate(loaded_date=today.strftime("%A, %B %d, %Y"), raw_data=corr_data)
htmlTemplate.render()