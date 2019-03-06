import numpy as np
import pandas as pd

from exchange.poloniex.poloniex import PoloniexWrapper


class ExchangeDatabase(object):

    def __init__(self):
        self.exchanges = pd.DataFrame(
            [PoloniexWrapper()], columns=['Exchange'])
        self.register_currency_pairs()
        self.register_tradable_pairs()
        self.chart_data = pd.DataFrame(
            columns=['Close', 'Date', 'High', 'Low', 'Open', 'Exchange', 'Currency Pair', 'Period'])

    def register_currency_pairs(self):
        for _, row in self.exchanges.iterrows():
            exchange = row['Exchange']
            currency_pairs = exchange.get_currency_pairs()
            self.currency_pairs = pd.DataFrame(
                np.array([currency_pairs, [exchange.EXCHANGE_NAME] * len(currency_pairs)]).T, columns=['Currency Pair', 'Exchange'])

    def register_tradable_pairs(self):
        for _, row in self.exchanges.iterrows():
            exchange = row['Exchange']
            tradable_pairs = list(exchange.get_tradable_pairs())
            self.tradable_pairs = pd.DataFrame(
                np.array([tradable_pairs, [exchange.EXCHANGE_NAME] * len(tradable_pairs)]).T, columns=['Tradable Pair', 'Exchange'])

    def get_chart_data(self, exchange, currency_pair, date, period):
        return self.chart_data[(self.chart_data['Date'] == date) & (self.chart_data['Currency Pair'] == currency_pair) & (self.chart_data['Exchange'] == exchange) & (self.chart_data['Period'] == period)]

    def register_chart_data(self, exchange, currency_pair, period, start, end):
        for date in range(start, end, period):
            if not ((self.chart_data['Date'] == date) & (self.chart_data['Currency Pair'] == currency_pair) & (self.chart_data['Exchange'] == exchange) & (self.chart_data['Period'] == period)).any():
                for _, row in self.exchanges.iterrows():
                    if row['Exchange'].EXCHANGE_NAME == exchange:
                        exchange = row['Exchange']
                        chart_data = exchange.get_chart_data(
                            currency_pair, period, date, end)
                        chart_data['Exchange'] = pd.Series(
                            [exchange.EXCHANGE_NAME] * len(chart_data))
                        chart_data['Currency Pair'] = pd.Series(
                            [currency_pair] * len(chart_data))
                        chart_data['Period'] = pd.Series(
                            [period] * len(chart_data))
                        self.chart_data = self.chart_data.append(chart_data)
                break

    def is_tradable_pair(self, exchange, tradable_pair):
        return (self.tradable_pairs == np.array([tradable_pair, exchange])).all(1).any()

    def is_valid_currency_pair(self, exchange, currency_pair):
        return (self.currency_pairs == np.array([exchange, currency_pair])).all(1).any()

    def is_valid_exchange(self, exchange):
        for _, row in self.exchanges.iterrows():
            if row['Exchange'].EXCHANGE_NAME == exchange:
                return True
        return False
