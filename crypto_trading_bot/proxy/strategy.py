from exchange.exchange_db import ExchangeDatabase


class Strategy(object):
    def __init__(self, conn, exchange, pair, period, start, end):
        self.dates = [date for date in range(start, end + period, period)]
        self.idx = 0
        self.conn = conn
        self.exchange = exchange
        self.period = period
        self.pair = pair
        ExchangeDatabase().register_chart_data(exchange, pair, period, start, end)

    def tick(self):
        data = ExchangeDatabase().get_chart_data(
            self.exchange, self.pair, self.period, self.dates[self.idx]
        )
        if data is not None:
            high, low, open, close, weighted_average = data
            self.conn.socket.send(
                str(
                    {
                        "eventType": "NEW_CANDLESTICK",
                        "payload": {
                            "high": high,
                            "low": low,
                            "open": open,
                            "close": close,
                            "weighted_average": weighted_average,
                        },
                    }
                ).encode()
            )
        else:
            self.conn.socket.send(
                {"eventType": "ERROR_CHART_DATA_DOES_NOT_EXIST", "payload": {}}
            )
        self.idx += 1
