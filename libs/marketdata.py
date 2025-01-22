import redis.exceptions
from yflive import QuoteStreamer
import yaml
from pathlib import Path
import os
import redis
import sys

CONFIG_DIR_PATH = r"C:\Users\User\Desktop\projects\trading\configs"

class MarketData:
    
    def __init__(self, configPath=None, configfile=None):
        configPath = configPath or CONFIG_DIR_PATH
        configfile = configfile or "marketdata.yaml"
        self.config = self._read_config(configPath=configPath, configfile=configfile)
        self.redis_client = redis.StrictRedis(
            host=self.config['redis']['host'],
            port=self.config['redis']['port'],
            db=self.config['redis']['db']
        )
        self.channel = self.config['redis']['channel']
        #self.redis_client.ping()
            
    
    def _read_config(self, configPath, configfile):
        config_full_path = os.path.join(configPath, configfile )
        print(f"reading...{config_full_path}")
        return yaml.safe_load( Path( config_full_path ).read_text() )
    
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
    configPath = None
    configFile = None
    if len(sys.argv) > 1:
        configPath = sys.argv[1]
    if len(sys.argv) > 2:
        configFile = sys.argv[2]
    md = MarketData(configPath=configPath, configfile=configFile)
    md.run()
        
if __name__ == "__main__":
    main()