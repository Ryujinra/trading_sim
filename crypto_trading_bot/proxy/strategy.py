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
        if self.idx > len(self.dates) - 1:
            # TODO: Remove strategy from proxy strategies
            self.conn.socket.send(str({"eventType": "END_OF_CHART_DATA"}).encode())
            return
        print("dates: {}, idx: {}".format(len(self.dates), self.idx))
        data = ExchangeDatabase().get_chart_data(
            self.exchange, self.pair, self.period, self.dates[self.idx]
        )
        if data is not None:
            high, low, open, close, weighted_average = data
            self.conn.socket.send(
                str(
                    {
                        "eventType": "NEW_CHART_DATA",
                        "payload": {
                            "candlestick": {
                                "high": high,
                                "low": low,
                                "open": open,
                                "close": close,
                                "weighted_average": weighted_average,
                            }
                        },
                    }
                ).encode()
            )
        else:
            self.conn.socket.send(
                str(
                    {"eventType": "ERROR_CHART_DATA_DOES_NOT_EXIST", "payload": {}}
                ).encode()
            )
        self.idx += 1
