import argparse

from proxy.proxy import Proxy
from client.scheduler import Scheduler
from client.proxy_api import ProxyAPI
from util.logger import logger


class Strategy1(ProxyAPI):
    def __init__(self):
        ProxyAPI.__init__(self, "POLONIEX", "BTC_XMR", 14400, 1488700800, 1517572800)

    def handler(self, data):
        high, low, open, close, weighted_average = data
        if weighted_average > 0.0263:
            logger.info("Making a sell order at price: {:.5f}".format(weighted_average))
            self.sell_order()
        else:
            logger.info("Making a buy order at price: {:.5f}".format(weighted_average))
            self.buy_order()

    def analyze(self):
        print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--proxy", help="instantiate the proxy server", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--strategies",
        help="begin the analysis of various test strategies",
        action="store_true",
    )
    args = parser.parse_args()
    if args.proxy:
        Proxy()
    elif args.strategies:
        Scheduler([Strategy1])
