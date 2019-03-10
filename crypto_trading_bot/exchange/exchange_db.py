import os
import mysql.connector
import pandas as pd

from exchange.poloniex.poloniex import PoloniexWrapper


table = {}
table['currency_pair'] = (
    """
    CREATE TABLE IF NOT EXISTS `currency_pair` (
        `exchange` VARCHAR(15) NOT NULL,
        `pair` VARCHAR(15) NOT NULL,
        PRIMARY KEY (`exchange`, `pair`)
    )
    """
)
table['chart_data'] = (
    """
    CREATE TABLE IF NOT EXISTS `chart_data` (
        `exchange` VARCHAR(15) NOT NULL,
        `pair` VARCHAR(15) NOT NULL,
        `period` INTEGER UNSIGNED NOT NULL,
        `date` BIGINT UNSIGNED NOT NULL,
        `high` DOUBLE UNSIGNED NOT NULL,
        `low` DOUBLE UNSIGNED NOT NULL,
        `open` DOUBLE UNSIGNED NOT NULL,
        `close` DOUBLE UNSIGNED NOT NULL,
        PRIMARY KEY (`exchange`, `pair`, `period`, `date`),
        FOREIGN key (`exchange`, `pair`) REFERENCES `currency_pair` (`exchange`, `pair`) ON DELETE CASCADE
    )
    """
)
table['temp_chart_data'] = (
    """
    CREATE TEMPORARY TABLE `temp_chart_data` (
        `exchange` VARCHAR(15) NOT NULL,
        `pair` VARCHAR(15) NOT NULL,
        `period` INTEGER UNSIGNED NOT NULL,
        `date` BIGINT UNSIGNED NOT NULL,
        PRIMARY KEY (`exchange`, `pair`, `period`, `date`)
    )
    """
)

query = {}
query['insert_currency_pair'] = (
    """
    INSERT IGNORE INTO `currency_pair` (`exchange`, `pair`) VALUES (%s, %s);
    """
)
query['insert_chart_data'] = (
    """
    INSERT IGNORE INTO `chart_data` (`exchange`, `pair`, `period`, `date`, `high`, `low`, `open`, `close`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
)
query['is_valid_currency_pair'] = (
    """
    SELECT EXISTS (SELECT * from `currency_pair` WHERE `exchange`=%s AND `pair`=%s)
    """
)
query['insert_temp_chart_data'] = (
    """
    INSERT IGNORE INTO `temp_chart_data` (`exchange`, `pair`, `period`, `date`) VALUES (%s, %s, %s, %s);
    """
)
query['compare_chart_data'] = (
    """
    SELECT `date` FROM `temp_chart_data` WHERE (`exchange`, `pair`, `period`, `date`) NOT IN (SELECT `exchange`, `pair`, `period`, `date` FROM `chart_data`)
    """
)
query['drop_temp_chart_data_table'] = (
    "DROP TEMPORARY TABLE `temp_chart_data`"
)
query['get_chart_data'] = (
    "SELECT `high`, `low`, `open`, `close` FROM `chart_data` WHERE `exchange`=%s AND `pair`=%s AND `period`=%s AND `date`=%s"
)


class DateRange(object):

    def __init__(self, period):
        self.reset()
        self.period = period
        self.date_ranges = []

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
                self.date_ranges.append((self.start, self.start))
            else:
                self.date_ranges.append((self.start, self.end))
            self.reset(date)

    def get_date_ranges(self):
        self.date_ranges.append(((self.start, self.end)))
        return self.date_ranges


class ExchangeDatabase(object):

    def __init__(self):
        mysql_host = os.environ.get('MYSQL_HOST')
        mysql_user = os.environ.get('MYSQL_USER')
        mysql_pass = os.environ.get('MYSQL_PASS')
        mysql_db = os.environ.get('MYSQL_DB')
        self.cnx = mysql.connector.connect(
            host=mysql_host, user=mysql_user, password=mysql_pass, db=mysql_db)
        self.cursor = self.cnx.cursor()
        self.exchanges = {PoloniexWrapper.EXCHANGE_NAME: PoloniexWrapper()}
        # Instantiate the currency pair table.
        self.cursor.execute(table['currency_pair'])
        self.cnx.commit()
        # Instantiate the chart data table.
        self.cursor.execute(table['chart_data'])
        self.cnx.commit()
        self.register_currency_pairs()

    def register_currency_pairs(self):
        for exchange_name, exchange_instance in self.exchanges.items():
            pairs = exchange_instance.get_currency_pairs()
            data = list(
                zip([exchange_name] * len(pairs), pairs))
            self.cursor.executemany(query['insert_currency_pair'], data)
            self.cnx.commit()

    def register_chart_data(self, exchange, currency_pair, period, start, end):
        exchange = self.exchanges[exchange]
        data = pd.DataFrame()
        data['date'] = [date for date in range(start, end + period, period)]
        data['exchange'] = [exchange.EXCHANGE_NAME] * len(data)
        data['period'] = [period] * len(data)
        data['pair'] = [currency_pair] * len(data)
        data = data.reindex(columns=['exchange', 'pair', 'period', 'date'])
        self.cursor.execute(table['temp_chart_data'])
        self.cnx.commit()
        self.cursor.executemany(query['insert_temp_chart_data'], [
                                tuple(data) for data in data.values])
        self.cnx.commit()
        date_range = DateRange(period)
        self.cursor.execute(query['compare_chart_data'])
        for date in self.cursor:
            date_range.next(date[0])
        self.cursor.execute(query['drop_temp_chart_data_table'])
        self.cnx.commit()
        for start, end in date_range.get_date_ranges():
            if start is None and end is None:
                break
            elif end is None:
                end = start
            data = exchange.get_chart_data(currency_pair, period, start, end)
            data['exchange'] = [exchange.EXCHANGE_NAME] * len(data)
            data['period'] = [period] * len(data)
            data['pair'] = [currency_pair] * len(data)
            data['date'] = [date for date in range(
                start, end + period, period)]
            data = data.reindex(
                columns=['exchange', 'pair', 'period', 'date', 'high', 'low', 'open', 'close'])
            data = [tuple(data) for data in data.values]
            self.cursor.executemany(query['insert_chart_data'], data)
            self.cnx.commit()

    def is_valid_currency_pair(self, exchange, pair):
        self.cursor.execute(query['is_valid_currency_pair'], (exchange, pair))
        for data in self.cursor:
            return data[0] != False

    def get_chart_data(self, exchange, pair, period, date):
        self.cursor.execute(query['get_chart_data'], (exchange, pair, period, date))
        for data in self.cursor:
            return data

    def is_valid_exchange(self, exchange):
        return exchange in self.exchanges
