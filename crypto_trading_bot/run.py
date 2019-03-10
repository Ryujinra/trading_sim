from exchange.exchange_db import ExchangeDatabase
from proxy.proxy import Proxy

if __name__ == "__main__":
    Proxy()
    # exchange_db = ExchangeDatabase()
    # exchange_db.register_chart_data(
    #     'Poloniex', 'BTC_XMR', 14400, 1517500800, 1517500800 + 200 * 14400)
    # exchange_db.register_chart_data(
    #     'Poloniex', 'BTC_XMR', 14400, 1546372800 + 800 * 14400, 1546430400)
    # exchange_db.register_chart_data(
    #     'Poloniex', 'BTC_XMR', 14400, 1412380800, 1551470400)
    # exchange_db.is_valid_currency_pair('Poloniex', 'BTC_XMR')
