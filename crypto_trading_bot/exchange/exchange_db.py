import os
import mysql.connector
import sqlalchemy

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
        self.cnx.commit()
        self.cursor.execute('DROP TABLE chart_data')
        self.cnx.commit()
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
        data = exchange.get_chart_data(currency_pair, period, start, end)
        data['exchange'] = [exchange.EXCHANGE_NAME] * len(data)
        data['period'] = [period] * len(data)
        data['pair'] = [currency_pair] * len(data)
        data['date'] = [date for date in range(start, end + period, period)]
        data = data.reindex(
            columns=['exchange', 'pair', 'period', 'date', 'high', 'low', 'open', 'close'])
        data = [tuple(data) for data in data.values]
        self.cursor.executemany(query['insert_chart_data'], data)
        self.cnx.commit()

    def is_valid_currency_pair(self, exchange, pair):
        self.cursor.execute(query['is_valid_currency_pair'], (exchange, pair))
        for data in self.cursor:
            return data[0] != False

    def is_valid_exchange(self, exchange):
        return exchange in self.exchanges
