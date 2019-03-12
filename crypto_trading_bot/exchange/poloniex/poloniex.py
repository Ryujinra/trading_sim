import os
import hashlib
import hmac
import time
import json
import urllib
import requests
import numpy as np
import pandas as pd

from util.logger import logger
from ..util.exchange_logger import exchange_logger
from ..util.exchange_api import ExchangeAPI


class PoloniexPublicWrapper(ExchangeAPI):

    EXCHANGE_NAME = "POLONIEX"

    PUBLIC_URL = "https://poloniex.com/public"

    def query_public(self, command, **kwargs):
        kwargs["command"] = command
        return requests.Session().get(self.PUBLIC_URL, params=kwargs).json()

    @exchange_logger
    def get_currency_pairs(self):
        return list(self.query_public("returnTicker"))

    @exchange_logger
    def get_chart_data(self, currency_pair, period, start, end):
        chart_data = self.query_public(
            "returnChartData",
            currencyPair=currency_pair,
            period=period,
            start=start,
            end=end,
        )
        return pd.DataFrame(chart_data).drop(columns=["volume", "quoteVolume"])


class PoloniexWrapper(PoloniexPublicWrapper):

    PRIVATE_URL = "https://poloniex.com/tradingApi"

    def __init__(self):
        self.api_key = os.environ.get("POLONIEX_API_KEY")
        self.secret = os.environ.get("POLONIEX_SECRET")
        if self.api_key is None or self.secret is None:
            logger.fatal("Failed to load the Poloniex API keys.")
            exit()

    def query_private(self, command):
        data = {"command": command, "nonce": int(time.time() * 1000)}
        sig = hmac.new(
            str.encode(self.secret, "utf-8"),
            str.encode(urllib.parse.urlencode(data), "utf-8"),
            hashlib.sha512,
        )
        req = requests.Session()
        headers = req.headers.update({"Key": self.api_key, "Sign": sig.hexdigest()})
        res = req.post(self.PRIVATE_URL, data=data)
        return res.json()

    @exchange_logger
    def get_tradable_pairs(self):
        return self.query_private("returnTradableBalances")
