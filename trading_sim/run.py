import argparse

from proxy.proxy import Proxy
from client.dispatcher import Dispatcher
from client.strategy import Strategy

# Example strategy...
def strategy():
    # Instantiate the Strategy generator.
    strategy = Strategy("POLONIEX", "BTC_XMR", 14400, 1488700800, 1517572800)
    for high, low, open, close, weighted_average in strategy:
        threshold = 0.0263
        # Place a sell order when the candlestick average is above a certain
        # threshold.
        if weighted_average > threshold:
            strategy.new_sell_order()
        # Likewise, place a buy order when the candlestick is below a certain threshold.
        else:
            strategy.new_buy_order()


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
        Proxy()  # Instantiate the Proxy.
    elif args.dispatch:
        # Example...
        # Dispatch a list of strategies...
        Dispatcher([strategy, strategy, strategy])
