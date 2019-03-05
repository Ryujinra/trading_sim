from exchange.poloniex.poloniex import PoloniexPrivateWrapper
from proxy.proxy import Proxy

if __name__ == '__main__':
    data = PoloniexPrivateWrapper().is_currency_pair('BTC_XMR')
    print(data)
