from tabulate import tabulate
from config import Config
import ccxt


class Trading:

    @staticmethod
    def book(exchange, pair):
        exchanges = Config().exchanges
        if exchange not in exchanges:
            print("Error: Exchange ", exchange, " was not found or not configured")
            return
        client = exchanges[exchange]['client']
        orders = client.fetch_order_book(pair)
        d = []
        zipped_orders = list(zip(orders['bids'], orders['asks']))
        for i, (bid, ask) in enumerate(zipped_orders):
            d.append([bid[0], bid[1], ask[0], ask[1]])
            if i > 10:
                break
        print(tabulate(d, headers=["Bid Price", "Bid Volume", "Ask Price", "Ask Volume"]))

    @staticmethod
    def create_order(exchange, pair, side, amount=0, price=None):
        exchanges = Config().exchanges
        if exchange not in exchanges:
            print("Error: Exchange ", exchange, " was not found or not configured")
            return
        if side not in ['sell', 'buy']:
            print("Error: Operation doesn't support ", side)
            return
        client = exchanges[exchange]['client']
        if client.has['createOrder']:
            if amount == 0 and side == 'sell':
                [coin, _] = pair.split('/')
                balance = client.fetch_balance()
                if coin not in balance['free']:
                    print("Error: Can't find coin ", coin, "in the wallet")
                    return
                amount = balance['free'][coin]
            elif amount == 0 and side == 'buy':
                [_, base] = pair.split('/')
                balance = client.fetch_balance()
                if base not in balance['free']:
                    print("Error: Can't find coin ", base, "in the wallet")
                    return
                tickers = client.fetch_tickers()
                coin_price = tickers[pair]["close"]
                amount = balance[base]['free'] / coin_price

            if price is None:
                res = client.create_order(pair, 'market', side.lower(), amount)
            else:
                res = client.create_order(pair, 'limit', side.lower(), amount, price)
            print(res)
        else:
            print("Error: Exchange ", exchange, " doesn't support creating orders")
            return

    @staticmethod
    def list_orders(exchange, pair):
        exchanges = Config().exchanges
        if exchange not in exchanges:
            print("Error: Exchange ", exchange, " was not found or not configured")
            return
        client = exchanges[exchange]['client']
        d = []
        if client.has['fetchOrders']:
            orders = client.fetch_orders(pair)
            for order in orders:
                d.append([
                    pair,
                    order['info']['orderId'],
                    order['info']['type'],
                    order['info']['side'],
                    order['info']['price'],
                    order['info']['origQty'],
                    order['info']['fee'] if 'fee' in order['info'] else 0,
                    order['status'],
                ])
            print(tabulate(d, headers=["Pair", "ID", "Type", "Side", "Price", "Quantity", "Fees",  "Status"]))
        else:
            print('Error: Exchange ', exchange, "doesn't support fetchOrders")

    @staticmethod
    def cancel_order(exchange, pair, order_id):
        exchanges = Config().exchanges
        if exchange not in exchanges:
            print("Error: Exchange ", exchange, " was not found or not configured")
            return
        client = exchanges[exchange]['client']
        client.cancel_order(pair, order_id)
