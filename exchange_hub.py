from config import Config


class ExchangeHub:

    @staticmethod
    def exchanges():
        exchanges = Config().exchanges
        for exchange in exchanges:
            print(exchange)

