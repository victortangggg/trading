import redis.exceptions
from yflive import QuoteStreamer
import yaml
from pathlib import Path
import os
import redis

CONFIG_DIR_PATH = r"C:\Users\User\Desktop\projects\trading\configs"

class MarketData:
    
    def __init__(self, configfile="marketdata.yaml"):
        self.config = self._read_config(configfile=configfile)
        self.redis_client = redis.StrictRedis(
            host=self.config['redis']['host'],
            port=self.config['redis']['port'],
            db=self.config['redis']['db']
        )
        self.channel = self.config['redis']['channel']
        self.redis_client.ping()
            
    
    def _read_config(self, configfile):
        return yaml.safe_load( Path( os.path.join(CONFIG_DIR_PATH, configfile ) ).read_text() )
    
    def _on_quote(self, quote):
        #print(f"received: { quote }")
        message = ":".join([ f"{ field }={ quote.__getattr__(field) }" for field in quote.__fields__ if quote.__getattr__(field) ])
        self.redis_client.publish(channel=self.channel, message=message)
        
    def run(self):
        quoteStreamer = QuoteStreamer()
        print(f"subscribing: { self.config['symbols'] }")
        quoteStreamer.subscribe( self.config['symbols'] )
        quoteStreamer.on_quote = lambda qs, q: self._on_quote(q)
        quoteStreamer.start(should_thread=False)
        
        
def main():
    md = MarketData()
    md.run()
        
if __name__ == "__main__":
    main()