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
