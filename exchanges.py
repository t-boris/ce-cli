from tabulate import tabulate

from config import Config


class ExchangeHub:

    @staticmethod
    def exchanges():
        d = []
        exchanges = Config().exchanges
        for exchange in exchanges:
            client = exchanges[exchange]['client']
            failed_connection = False
            try:
                client.fetch_balance()
            except Exception:
                failed_connection = True

            d.append([exchange, "OK" if not failed_connection else "FAILED"])

        print(tabulate(d, headers=["Exchange", "Status"]))


