import os
import json
import logging

from poloniex import Poloniex
from enum import Enum

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ExchangeType(Enum):

    POLONIEX = 'POLONIEX'

    def is_valid(test_exchange):
        for exchange in ExchangeType:
            if exchange.name == test_exchange:
                return True
        return False


class PoloniexWrapper(object):

    def __init__(self):
        api_key = os.environ.get('POLONIEX_API_KEY')
        secret = os.environ.get('POLONIEX_SECRET')
        if api_key is None or secret is None:
            logger.fatal('Failed to load the Poloniex API keys.')
            exit()
        self.poloniex = Poloniex(api_key, secret)

    def get_tradable_balances(self):
        print(self.poloniex.returnBalances())


if __name__ == '__main__':
    PoloniexWrapper().get_tradable_balances()
