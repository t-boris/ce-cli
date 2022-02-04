from config import Config
from tabulate import tabulate


class Balance:

    @staticmethod
    # Returns balance for given exchange
    def exchange(name, showZero=False):
        d = []
        exchanges = Config().exchanges
        if exchanges.get(name) is None:
            print("Error: Can't find exchange ", name, " in config file")
            return
        client = exchanges[name]['client']
        balance = client.fetch_balance()
        for coin in balance['total']:
            total = balance['total'][coin]
            used = balance['used'][coin]
            free = balance['free'][coin]
            if total == 0 and not showZero:
                continue
            d.append([coin, free, used, total])
        print(tabulate(d, headers=["Coin", "Free", "Used", "Total"]))
