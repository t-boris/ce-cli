from tabulate import tabulate

from config import Config


class ExchangeHub:

    @staticmethod
    def exchanges():
        d = []
        exchanges = Config().exchanges
        for exchange in exchanges:
            d.append([exchange])

        print(tabulate(d, headers=["Exchange"]))


