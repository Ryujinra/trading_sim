import pandas as pd
from threading import Lock
import sqlite3

from exchange.poloniex import PoloniexWrapper


table = {}
table[
    "currency_pair"
] = """
    CREATE TABLE IF NOT EXISTS currency_pair (
        exchange VARCHAR(15) NOT NULL,
        pair VARCHAR(15) NOT NULL,
        PRIMARY KEY (exchange, pair)
    )
    """
table[
    "chart_data"
] = """
    CREATE TABLE IF NOT EXISTS chart_data (
        exchange VARCHAR(15) NOT NULL,
        pair VARCHAR(15) NOT NULL,
        period INTEGER UNSIGNED NOT NULL,
        date BIGINT UNSIGNED NOT NULL,
        high DOUBLE UNSIGNED NOT NULL,
        low DOUBLE UNSIGNED NOT NULL,
        open DOUBLE UNSIGNED NOT NULL,
        close DOUBLE UNSIGNED NOT NULL,
        weightedAverage DOUBLE UNSIGNED NOT NULL,
        PRIMARY KEY (exchange, pair, period, date),
        FOREIGN key (exchange, pair) REFERENCES currency_pair (exchange, pair) ON DELETE CASCADE
    )
    """
table[
    "temp_chart_data"
] = """
    CREATE TEMPORARY TABLE temp_chart_data (
        exchange VARCHAR(15) NOT NULL,
        pair VARCHAR(15) NOT NULL,
        period INTEGER UNSIGNED NOT NULL,
        date BIGINT UNSIGNED NOT NULL,
        PRIMARY KEY (exchange, pair, period, date)
    )
    """

query = {}
query[
    "insert_currency_pair"
] = """
    INSERT OR IGNORE INTO currency_pair VALUES (?, ?)
    """
query[
    "insert_chart_data"
] = """
    INSERT OR IGNORE INTO chart_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
query[
    "is_valid_currency_pair"
] = """
    SELECT EXISTS (SELECT * from currency_pair WHERE exchange=? AND pair=?)
    """
query[
    "insert_temp_chart_data"
] = """
    INSERT OR IGNORE INTO temp_chart_data VALUES (?, ?, ?, ?)
    """
query[
    "compare_chart_data"
] = """
    SELECT date FROM temp_chart_data WHERE (exchange, pair, period, date) NOT IN (SELECT exchange, pair, period, date FROM chart_data)
    """
query["drop_temp_chart_data_table"] = "DROP TABLE temp_chart_data"
query[
    "get_chart_data"
] = "SELECT high, low, open, close, weightedAverage FROM chart_data WHERE exchange=? AND pair=? AND period=? AND date=?"


class Window(object):
    def __init__(self, period):
        self.reset()
        self.period = period
        self._date_ranges = []

    def reset(self, start=None):
        self.start = start
        self.end = None
        self.counter = 1

    def next(self, date):
        if self.start is None:
            self.start = date
        elif self.start + (self.period * self.counter) == date:
            self.end = date
            self.counter += 1
        else:
            if self.end is None:
                self._date_ranges.append((self.start, self.start))
            else:
                self._date_ranges.append((self.start, self.end))
            self.reset(date)

    @property
    def date_ranges(self):
        self._date_ranges.append(((self.start, self.end)))
        return self._date_ranges


class ExchangeDatabase(object):
    class __ExchangeDatabase(object):
        def __init__(self):
            self.mutex = Lock()
            self.cnx = sqlite3.connect("trading_sim.db", check_same_thread=False)
            self.cursor = self.cnx.cursor()
            self.exchanges = {PoloniexWrapper.EXCHANGE_NAME: PoloniexWrapper()}
            # Instantiate the currency pair table.
            self.cursor.execute(table["currency_pair"])
            self.cnx.commit()
            # Instantiate the chart data table.
            self.cursor.execute(table["chart_data"])
            self.cnx.commit()
            # Register currency pairs.
            for exchange_name, exchange_instance in self.exchanges.items():
                pairs = exchange_instance.get_currency_pairs()
                data = list(zip([exchange_name] * len(pairs), pairs))
                self.cursor.executemany(query["insert_currency_pair"], data)
                self.cnx.commit()
            print("done")

        def register_chart_data(self, exchange, currency_pair, period, start, end):
            print("start register_chart_data")
            exchange = self.exchanges[exchange]
            data = pd.DataFrame()
            data["date"] = [date for date in range(start, end + period, period)]
            data["exchange"] = [exchange.EXCHANGE_NAME] * len(data)
            data["period"] = [period] * len(data)
            data["pair"] = [currency_pair] * len(data)
            data = data.reindex(columns=["exchange", "pair", "period", "date"])
            window = Window(period)
            with self.mutex:
                self.cursor.execute(table["temp_chart_data"])
                self.cnx.commit()
                self.cursor.executemany(
                    query["insert_temp_chart_data"],
                    [tuple(data) for data in data.values],
                )
                self.cnx.commit()
                self.cursor.execute(query["compare_chart_data"])
                for date in self.cursor:
                    window.next(date[0])
                self.cursor.execute(query["drop_temp_chart_data_table"])
                self.cnx.commit()
            for start, end in window.date_ranges:
                if start is None and end is None:
                    break
                elif end is None:
                    end = start
                data = exchange.get_chart_data(currency_pair, period, start, end)
                data["exchange"] = [exchange.EXCHANGE_NAME] * len(data)
                data["period"] = [period] * len(data)
                data["pair"] = [currency_pair] * len(data)
                data["date"] = [
                    date
                    for date in range(
                        end - period * (len(data) - 1), end + period, period
                    )
                ]
                data = data.reindex(
                    columns=[
                        "exchange",
                        "pair",
                        "period",
                        "date",
                        "high",
                        "low",
                        "open",
                        "close",
                        "weightedAverage",
                    ]
                )
                data = [tuple(data) for data in data.values]
                with self.mutex:
                    self.cursor.executemany(query["insert_chart_data"], data)
                    self.cnx.commit()
            print("done register_chart_data")

        def is_valid_currency_pair(self, exchange, pair):
            print("start is_valid_currency_pair")
            with self.mutex:
                self.cursor.execute(query["is_valid_currency_pair"], (exchange, pair))
                for data in self.cursor:
                    return data[0] != False
            print("done is_valid_currency_pair")

        def get_chart_data(self, exchange, pair, period, date):
            print("start get_chart_data")
            with self.mutex:
                self.cursor.execute(
                    query["get_chart_data"], (exchange, pair, period, date)
                )
                for data in self.cursor:
                    return data
            print("done get_chart_data")

        def is_valid_exchange(self, exchange):
            return exchange in self.exchanges

    instance = None

    def __init__(self):
        if not ExchangeDatabase.instance:
            ExchangeDatabase.instance = ExchangeDatabase.__ExchangeDatabase()

    def __getattr__(self, name):
        return getattr(self.instance, name)
