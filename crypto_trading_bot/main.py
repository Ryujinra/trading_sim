from exchange.exchange_db import ExchangeDatabase
from proxy.proxy import Proxy

if __name__ == '__main__':
    exchange_db = ExchangeDatabase()
    exchange_db.register_chart_data('Poloniex',
                                    'BTC_XMR', 14400, 1546300800, 1546646400)
    exchange_db.register_chart_data('Poloniex',
                                    'BTC_XMR', 14400, 1546300800, 1546646400 + 14400 * 5)
