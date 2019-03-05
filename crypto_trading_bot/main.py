from exchange.poloniex.poloniex import PoloniexPrivateWrapper

if __name__ == '__main__':
    print(PoloniexPrivateWrapper().get_chart_data(
        'BTC_XMR', 14400, 1546300800, 1546646400))
