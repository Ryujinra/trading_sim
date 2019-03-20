import argparse

from proxy.proxy import Proxy
from client.dispatcher import Dispatcher
from client.strategy import Strategy


class Example1(Strategy):
    def __init__(self):
        super().__init__("POLONIEX", "BTC_XMR", 14400, 1488700800, 1488988800)

    def handler(self, data):
        high, low, open, close, weighted_average, volume = data
        threshold = 0.01158483
        # Place a sell order when the candlestick average is above a certain
        # threshold.
        if weighted_average > threshold:
            self.new_sell_order()
        # Likewise, place a buy order when the candlestick is below a certain threshold.
        else:
            self.new_buy_order()


class Example2(Strategy):
    def __init__(self):
        super().__init__("POLONIEX", "BTC_ETH", 14400, 1488700800, 1488988800)

    def handler(self, data):
        high, low, open, close, weighted_average, volume = data
        threshold = 0.01511201
        # Place a sell order when the candlestick average is above a certain
        # threshold.
        if weighted_average > threshold:
            self.new_sell_order()
        # Likewise, place a buy order when the candlestick is below a certain threshold.
        else:
            self.new_buy_order()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--proxy", help="instantiate the proxy server", action="store_true"
    )
    parser.add_argument(
        "-d",
        "--dispatch",
        help="dispatch the strategies for execution",
        action="store_true",
    )
    args = parser.parse_args()
    if args.proxy:
        # Instantiate the Proxy.
        Proxy()
    elif args.dispatch:
        # Dispatch a list of strategies.
        Dispatcher([Example1, Example1, Example2])
