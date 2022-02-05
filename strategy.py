import time

from tabulate import tabulate

from bot import Bot
from config import Config
import ccxt


def get_compressed_orders(orders, min_coin_amount):
    bids = orders['bids']
    asks = orders['asks']
    volume = 0
    total_price = 0
    for bid in bids:
        volume += bid[1]
        total_price += bid[0] * bid[1]
        if volume > min_coin_amount:
            break
    bid_price = total_price / volume
    bid_volume = volume
    volume = 0
    total_price = 0
    for ask in asks:
        volume += ask[1]
        total_price += ask[0] * ask[1]
        if volume > min_coin_amount:
            break
    ask_price = total_price / volume
    ask_volume = volume

    return bid_price, bid_volume, ask_price, ask_volume


class Strategy:
    def __init__(self):
        self.bot = Bot()

    def arbitrage(self, exchange_a, exchange_b, pair, min_coin_amount=0.01, dryRun=True):
        exchanges = Config().exchanges
        if exchange_a not in exchanges:
            print("Error: Exchange", exchange_a, "was not found or not configured")
            return
        if exchange_b not in exchanges:
            print("Error: Exchange", exchange_b, "was not found or not configured")
            return
        client_a = exchanges[exchange_a]['client']
        client_b = exchanges[exchange_b]['client']
        orders_a = client_a.fetch_order_book(pair)
        orders_b = client_b.fetch_order_book(pair)

        max_bid_a, bid_volume_a, min_ask_a, ask_volume_a = get_compressed_orders(orders_a, min_coin_amount)
        max_bid_b, bid_volume_b, min_ask_b, ask_volume_b = get_compressed_orders(orders_b, min_coin_amount)

        [coin, base] = pair.split('/')

        if min_ask_a < max_bid_b:
            # TODO: use current balance instead of 1
            volume = min(ask_volume_a, bid_volume_b)
            transaction_fee_percent_a = client_a.fees['trading']['taker']
            transaction_fee_percent_b = client_b.fees['trading']['taker']
            coin_info = client_a.fetch_currencies()[coin]['info']
            if isinstance(coin_info, list) and len(coin_info) > 0 and 'fee' in coin_info[0]:
                coin_transfer_fee = coin_info[0]['fee']
            else:
                coin_transfer_fee = 0
            base_info = client_b.fetch_currencies()[base]['info']
            if isinstance(base_info, list) and len(base_info) > 0 and 'fee' in base_info[0]:
                base_transfer_fee = base_info[0]['fee']
            else:
                base_transfer_fee = 0
            # Buy  on exchange A -> + coin (volume) - base (volume * buy price * (1-transaction_fee_percent_a))
            # Sell on exchange B -> - coin (volume) + base (volume * sell price * (1 + transaction_fee_percent_b))
            base_left = volume * (max_bid_b * (1 - transaction_fee_percent_a) -
                                  min_ask_a * (1 + transaction_fee_percent_b)) - base_transfer_fee - \
                        (float(coin_transfer_fee) * max_bid_a)
            profit = 100 * base_left / (volume*min_ask_a)
            if dryRun:
                print(tabulate([[profit, base_left, exchange_a, min_ask_a, exchange_b, max_bid_b]],
                               headers=["Profit %", "Base Coin Earned", "Buy On", "Buy Price", "Sell On", "Sell Price"]))
            else:
                self.bot.execute_arbitrage(pair, exchange_a, min_ask_a, exchange_b, max_bid_b, volume)

        elif min_ask_b < max_bid_a:
            # TODO: use current balance instead of 1
            volume = min(ask_volume_b, bid_volume_a)
            transaction_fee_percent_a = client_a.fees['trading']['taker']
            transaction_fee_percent_b = client_b.fees['trading']['taker']
            if isinstance(client_b.fetch_currencies()[coin]['info'], list) and \
                    len(client_b.fetch_currencies()[coin]['info']) > 0 and \
                    'fee' in client_b.fetch_currencies()[coin]['info'][0]:
                coin_transfer_fee = client_b.fetch_currencies()[coin]['info'][0]['fee']
            else:
                coin_transfer_fee = 0
            if isinstance(client_a.fetch_currencies()[base]['info'], list) and \
                    len(client_a.fetch_currencies()[base]['info']) > 0 and \
                    'fee' in client_a.fetch_currencies()[base]['info'][0]:
                base_transfer_fee = client_a.fetch_currencies()[base]['info'][0]['fee']
            else:
                base_transfer_fee = 0

            # Sell on exchange A -> - coin (volume) + base (volume * sell price * (1 - transaction_fee_percent_a))
            # Buy  on exchange B -> + coin (volume) - base (volume * buy price * (1 + transaction_fee_percent_b))
            base_left = volume * (max_bid_a * (1 - transaction_fee_percent_a) -
                                  min_ask_b * (1 + transaction_fee_percent_b)) - base_transfer_fee - \
                        (float(coin_transfer_fee) * max_bid_b)
            profit = 100 * base_left / (volume * min_ask_b)

            if dryRun:
                print(tabulate([[profit, base_left, exchange_b, min_ask_b, exchange_a, max_bid_a]],
                               headers=["Profit %", "Base Coin Earned", "Buy On", "Buy Price", "Sell On", "Sell Price"]))
            else:
                self.bot.execute_arbitrage(pair, exchange_b, min_ask_b, exchange_a, max_bid_a, volume)

        else:
            print('Arbitrage is not possible. You can buy for', min(min_ask_a, min_ask_b),
                  'and sell for', min(max_bid_a, max_bid_b))

    def arbitrage_poll(self, exchange_a, exchange_b, pair, min_coin_amount=0.01, dryRun=True):
        while True:
            self.arbitrage(exchange_a, exchange_b, pair, min_coin_amount, dryRun)
            time.sleep(1)
