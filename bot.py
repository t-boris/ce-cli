from config import Config
from trading import Trading


class Bot:
    def __init__(self):
        self.exchanges = Config().exchanges
        self.trading = Trading()

    def execute_arbitrage(self, pair, buy_exchange, buy_price, sell_exchange, sell_price, volume):
        client_buy = self.exchanges[buy_exchange]['client']
        client_sell = self.exchanges[sell_exchange]['client']
        [coin, base] = pair.split('/')

        # Check if on buyer side there is enough money
        balances_buy = client_buy.fetch_balance()
        if base not in balances_buy['free']:
            print("Error: Can't find coin ", base, "in the wallet")
            return
        base_buy = balances_buy['free'][base]
        if base_buy <= 0:
            print("Error: There is no free coin", base, "in the wallet on", buy_exchange)
            return
        can_buy_amount = base_buy / buy_price
        market = client_buy.markets[pair]
        min_order_size = market['limits']['amount']['min']
        if can_buy_amount < min_order_size:
            print("Error: Can't perform operation. Low resources. Coin ", base, " amount ", base_buy,
                  ". It's enough to buy ", can_buy_amount, "of", coin, ". Minimum amount is ", min_order_size)
            return

        # Check is enough coins on seller side
        balances_sell = client_sell.fetch_balance()
        if coin not in balances_sell['free']:
            print("Error: Can't find coin", coin, "in the wallet on", sell_exchange)
            return
        coin_sell = balances_sell['free'][coin]
        if coin_sell <= 0:
            print("Error: There is no free coin ", coin, "in the wallet")
            return
        can_sell_amount = min(volume, coin_sell)
        market = client_buy.markets[pair]
        min_order_size = market['limits']['amount']['min']
        if can_sell_amount < min_order_size:
            print("Error: Can't perform operation. Low resources. Coin ", coin, " amount ", coin_sell,
                  ". It's enough to buy ", can_sell_amount, "of", coin, ". Minimum amount is ", min_order_size)
            return

        volume = min(can_sell_amount, can_buy_amount)

        # Buy request
        self.trading.create_order(buy_exchange, pair, 'buy', volume, buy_price)
        # Sell request
        self.trading.create_order(sell_exchange, pair, 'sell', volume, sell_price)

        self.trading.list_orders(buy_exchange, pair)
        self.trading.list_orders(sell_exchange, pair)