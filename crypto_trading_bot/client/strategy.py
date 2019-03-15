from .proxy_api import ProxyAPI
from util.logger import logger


class Strategy(ProxyAPI):
    def __init__(self):
        ProxyAPI.__init__(self, "POLONIEX", "BTC_XMR", 14400, 1488700800, 1517572800)

    def strategy(self, high, low, open, close, weighted_average):
        if weighted_average > 0.0263:
            logger.info("Making a sell order at price: {:.5f}".format(weighted_average))
            self.sell_order()
        else:
            logger.info("Making a buy order at price: {:.5f}".format(weighted_average))
            self.buy_order()
