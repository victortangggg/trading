# from openbb_terminal.sdk import openbb
import logging
import argparse
from datetime import datetime
import pytz

LOG_DIR = "C:\\Users\\User\\Desktop\\projects\\trading\\logs"
logging.basicConfig(filename=f'LOG_DIR\\example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

today = datetime.now(pytz.timezone('America/New_York'))
logging.info(today)

parser = argparse.ArgumentParser(description="Download and store economic events")

# Add arguments
parser.add_argument("-s", "--start_date", help="Start date in YYYY-MM-DD format")
parser.add_argument("-e", "--end_date", help="End date in YYYY-MM-DD format")

# Parse the arguments
args = parser.parse_args()

# Print the values
logging.info(f"Start Date: { args.start_date }")
logging.info(f"End Date: { args.end_date }" )

# events_df = openbb.economy.events(countries=['united_states'], start_date='2000-01-01', end_date='2000-03-01')
# events_df.to_csv(path_or_buf='../data/US_2000_events.csv')

