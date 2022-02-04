import fire

from balance import Balance
from exchanges import ExchangeHub
from strategy import Strategy
from trading import Trading


class Command:
    def __init__(self):
        self.hub = ExchangeHub()
        self.balance = Balance()
        self.trade = Trading()
        self.strategy = Strategy()


if __name__ == "__main__":
    fire.Fire(Command)

