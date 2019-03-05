import os
import hashlib
import hmac
import time
import json
import urllib
import requests

from util.logger import logger
from ..util.exchange_logger import exchange_logger
from ..util.common import ExchangeAPI


class PoloniexPublicWrapper(ExchangeAPI):

    EXCHANGE_NAME = 'Poloniex'

    PUBLIC_URL = 'https://poloniex.com/public'

    def query_public(self, command, **kwargs):
        kwargs['command'] = command
        return requests.Session().get(
            self.PUBLIC_URL,
            params=kwargs).json()

    @exchange_logger
    def is_currency_pair(self, currency_pair):
        return currency_pair in list(self.query_public('returnTicker'))

    @exchange_logger
    def get_chart_data(self, currency_pair, period, start, end):
        return self.query_public('returnChartData',
                                 currencyPair=currency_pair, period=period, start=start, end=end)


class PoloniexPrivateWrapper(PoloniexPublicWrapper):

    PRIVATE_URL = 'https://poloniex.com/tradingApi'

    def __init__(self):
        self.api_key = os.environ.get('POLONIEX_API_KEY')
        self.secret = os.environ.get('POLONIEX_SECRET')
        if self.api_key is None or self.secret is None:
            logger.fatal('Failed to load the Poloniex API keys.')
            exit()

    def query_private(self, command):
        data = {'command': command, 'nonce': int(time.time() * 1000)}
        sig = hmac.new(
            str.encode(self.secret, 'utf-8'),
            str.encode(urllib.parse.urlencode(data), 'utf-8'),
            hashlib.sha512
        )
        req = requests.Session()
        headers = req.headers.update(
            {'Key': self.api_key, 'Sign': sig.hexdigest()})
        res = req.post(self.PRIVATE_URL, data=data)
        return res.json()

    @exchange_logger
    def get_balance(self, currency):
        balances = self.query_private('returnBalances')
        if currency in balances:
            return self.query_private('returnBalances')[currency]
        else:
            logger.fatal('Currency does not exist: {}'.format(currency))
