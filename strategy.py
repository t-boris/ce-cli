import time

from tabulate import tabulate

from bot import Bot
from config import Config
import ccxt


class Strategy:

    def __init__(self):
        self.bot = Bot()

    def arbitrage(self, exchange_a, exchange_b, pair, dryRun=True):
        exchanges = Config().exchanges
        if exchange_a not in exchanges:
            print("Exchange ", exchange_a, " was not found or not configured")
            return
        if exchange_b not in exchanges:
            print("Exchange ", exchange_b, " was not found or not configured")
            return
        client_a = exchanges[exchange_a]['client']
        client_b = exchanges[exchange_b]['client']
        orders_a = client_a.fetch_order_book(pair)
        orders_b = client_b.fetch_order_book(pair)

        # TODO: Calculate min/max bid/ask based on minimum amount
        max_bid_a = orders_a['bids'][0][0]
        min_ask_a = orders_a['asks'][0][0]
        max_bid_b = orders_b['bids'][0][0]
        min_ask_b = orders_b['asks'][0][0]

        if min_ask_a < max_bid_b:
            volume = min(orders_a['asks'][0][1], orders_b['bids'][0][1])
            if dryRun:
                print('Arbitrage is possible: Buy on ', exchange_a, ' sell on ', exchange_b)
                print("Buy for ", min_ask_a, " Sell for ", max_bid_b, ". Volume ", volume, ". Profit ",
                      (max_bid_b - min_ask_a) * 100 / min_ask_a)
            else:
                self.bot.execute_arbitrage(pair, exchange_a, min_ask_a, exchange_b, max_bid_b, volume)

        elif min_ask_b < max_bid_a:
            volume = min(orders_b['asks'][0][1], orders_a['bids'][0][1])
            if dryRun:
                print('Arbitrage is possible: Buy on ', exchange_b, ' sell on ', exchange_a)
                print("Buy for ", min_ask_b, " Sell for ", max_bid_a, ". Volume ", volume, ". Profit ",
                      (max_bid_a - min_ask_b) * 100 / min_ask_b)
            else:
                self.bot.execute_arbitrage(pair, exchange_b, min_ask_b, exchange_a, max_bid_a, volume)

        else:
            print('Arbitrage is not possible. You can buy for', min(min_ask_a, min_ask_b),
                  'and sell for', min(max_bid_a, max_bid_b))

    def arbitrage_poll(self, exchange_a, exchange_b, pair, dryRun=True):
        while True:
            self.arbitrage(exchange_a, exchange_b, pair, dryRun)
            time.sleep(2)
