from exchange.exchange_db import ExchangeDatabase


class Strategy(object):
    def __init__(self, conn, exchange, pair, period, start, end):
        self.running = True
        ExchangeDatabase().register_chart_data(exchange, pair, period, start, end)
        for date in range(start, end + period, period):
            if not self.running:
                break
            data = ExchangeDatabase().get_chart_data(exchange, pair, period, date)
            if data is not None:
                high, low, open, close = data
                data = {"high": high, "low": low, "open": open, "close": close}
                conn.socket.send(str(data).encode())
