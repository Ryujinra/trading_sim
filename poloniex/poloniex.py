import os
import hashlib
import hmac
import time
import json
import urllib
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Exchange(object):

    def get_balance(self, currency):
        pass

    def is_currency_pair(self, currency_pair):
        pass

    def get_chart_data(self, currency_pair, period, start, end):
        pass


class PoloniexPublic(Exchange):

    PUBLIC_URL = 'https://poloniex.com/public'

    def query_public(self, command, **kwargs):
        kwargs['command'] = command
        return requests.Session().get(
            self.PUBLIC_URL,
            params=kwargs).json()

    def is_currency_pair(self, currency_pair):
        logger.info('Querying the Poloniex API: {}'.format(
            self.is_currency_pair.__name__))
        return currency_pair in list(self.query_public('returnTicker'))

    def get_chart_data(self, currency_pair, period, start, end):
        logger.info('Querying the Poloniex API: {}'.format(
            self.get_chart_data.__name__))
        return self.query_public('returnChartData',
                                 currencyPair=currency_pair, period=period, start=start, end=end)


class PoloniexSecret(PoloniexPublic):

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

    def get_balance(self, currency):
        logger.info('Querying the Poloniex API: {}'.format(
            self.get_balance.__name__))
        balances = self.query_private('returnBalances')
        if currency in balances:
            return self.query_private('returnBalances')[currency]
        else:
            logger.fatal('Currency does not exist: {}'.format(currency))


if __name__ == '__main__':
    print(PoloniexSecret().get_chart_data(
        'BTC_XMR', 14400, 1546300800, 1546646400))
