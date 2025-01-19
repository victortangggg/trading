from libs.markets_corr import MarketRunningCorr, HTMLTemplate
from datetime import date, timedelta
import os
from win11toast import toast

MACRO_TICKERS = [
    'SHY', 
    'VXX', 
    'EWS', 
    'TQQQ', 
    'VOO',
    'GSG', 
    'UJB', 
    'TYD', 
    'GLD',
    'BTC-USD',
    'SGD=X',
]

SECTORS_TICKERS = [
    'XLY',
    'XLP',
    'XLE',
    'XLF',
    'XLV',
    'XLI',
    'XLB',
    'XLK',
    'XLU',
    'XME',
    'GDX',
    'IYR',
    'XHB',
    'XRT',
]

DATE_FORMAT = '%Y-%m-%d'
LOOKBACK = 30
APP_HTML_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\ui\\"
ARCHIVE_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\archive\\markets_corr\\"

today = date.today()
start_date_t0 = ( today - timedelta(days=LOOKBACK) ).strftime(DATE_FORMAT)

# past_html_path = APP_HTML_DIR + "markets_corr.html"
# yesterday = today - timedelta(days=1)
# archive_path = ARCHIVE_DIR + f"markets_corr.{yesterday.strftime(DATE_FORMAT)}.html"
# if os.path.exists( past_html_path ) and not os.path.exists( archive_path ):
#     os.rename( past_html_path, archive_path)

macros_running_corr = MarketRunningCorr(tickers=MACRO_TICKERS, start_date=start_date_t0)
macros_running_corr.run()
macro_corr_data_t0, macro_corr_changes, macro_changes_pct = macros_running_corr.get()
macro_last_date = macros_running_corr.last_date

sectors_running_corr = MarketRunningCorr(tickers=SECTORS_TICKERS, start_date=start_date_t0)
sectors_running_corr.run()
sectors_corr_data_t0, sectors_corr_changes, sectors_changes_pct = sectors_running_corr.get()
sectors_last_date = sectors_running_corr.last_date

htmlTemplate = HTMLTemplate(
    loaded_date=today.strftime("%A, %B %d, %Y"), 
    macro_last_date=macro_last_date.strftime("%A, %B %d, %Y"),
    raw_macro_corr_data=macro_corr_data_t0, 
    raw_macro_corr_changes=macro_corr_changes,
    raw_macro_changes_pct=macro_changes_pct,
    sectors_last_date=sectors_last_date.strftime("%A, %B %d, %Y"),
    raw_sectors_corr_data=sectors_corr_data_t0,
    raw_sectors_corr_changes=sectors_corr_changes,
    raw_sectors_changes_pct=sectors_changes_pct
)
htmlTemplate.render()
        
toast('Markets Correlation Report', button='Dismiss')