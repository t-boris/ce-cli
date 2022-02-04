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
            d.append([coin, used, free, total])
        print(tabulate(d, headers=["Coin", "Used", "Free", "Total"]))

    @staticmethod
    def total(showZero=False):
        d = []
        exchanges = Config().exchanges
        for exchange_name in exchanges:
            exchange = exchanges[exchange_name]
            client = exchange['client']
            balance = client.fetch_balance()
            for coin in balance['total']:
                total = balance['total'][coin]
                used = balance['used'][coin]
                free = balance['free'][coin]
                if total == 0 and not showZero:
                    continue
                coins_table = [x for x in d if x[0] == coin]
                if len(coins_table) == 0:
                    d.append([coin, used, free, total])
                else:
                    coin_table = coins_table[0]
                    coin_table[1] += used if used is not None else 0
                    coin_table[2] += free if free is not None else 0
                    coin_table[3] += total if total is not None else 0
        d.sort(key=lambda x: x[0])
        print(tabulate(d, headers=["Coin", "Used", "Free", "Total"]))

    @staticmethod
    def transfer(from_exchange, to_exchange, coin, amount=0):
        exchanges = Config().exchanges
        if from_exchange not in exchanges:
            print("Error: exchange", from_exchange, "is not configured")
            return
        if to_exchange not in exchanges:
            print("Error: exchange", to_exchange, "is not configured")
            return
        client = exchanges[from_exchange]['client']
        if amount <= 0:
            # Use all amount
            balance = client.fetch_balance()
            if coin not in balance['free']:
                print("Error: Can't find coin", coin, "in the wallet")
                return
            amount = balance['free'][coin]
        if coin.lower() not in exchanges[to_exchange]['wallet']:
            print("Error: Can't find", coin, "address for exchange", to_exchange)
            return
        address = exchanges[to_exchange]['wallet'][coin.lower()]
        try:
            res = client.withdraw(coin, amount, address)
            print(res)
        except Exception as e:
            print("Error: Failed to transfer", amount, "coins", coin, "from", from_exchange, "to", to_exchange)
            print(e)
