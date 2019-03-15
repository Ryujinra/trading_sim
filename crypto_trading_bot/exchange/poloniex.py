import json
import requests
import numpy as np
import pandas as pd

from util.logger import logger
from .util.exchange_logger import exchange_logger
from .util.exchange_api import ExchangeAPI


class PoloniexWrapper(ExchangeAPI):

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
