import ccxt
import yaml


class Config:
    def __init__(self):
        with open('exchanges.yaml', 'r') as file:
            self.exchanges = yaml.safe_load(file)
            for exchange in self.exchanges:
                exchange_class = getattr(ccxt, exchange)
                self.exchanges[exchange]['client'] = exchange_class({
                    'apiKey': self.exchanges[exchange]['apikey'],
                    'secret': self.exchanges[exchange]['secretkey'],
                })

    def get_exchanges(self):
        return self.exchanges
