import fire

from balance import Balance
from exchange_hub import ExchangeHub


class Command:
    def __init__(self):
        self.hub = ExchangeHub()
        self.balance = Balance()


if __name__ == "__main__":
    fire.Fire(Command)

