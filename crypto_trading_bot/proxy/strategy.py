import math
import json

from exchange.exchange_db import ExchangeDatabase
from .subscribable import Subscribable
from action.action_factory import ActionFactory


class PercentChange(object):
    def __init__(self):
        self.v1 = None
        self.v2 = None

    def is_complete(self):
        return self.v1 is not None and self.v2 is not None

    def set(self, v):
        if self.v1 is None:
            self.v1 = v
        else:
            self.v2 = v

    def compute_change(self):
        if self.is_complete():
            return ((self.v2 - self.v1) * 100) / math.fabs(self.v1)
        return 0


class Accumulator(object):
    def __init__(self):
        self.percent_changes = []

    def set(self, v):
        if not self.percent_changes or self.percent_changes[-1].is_complete():
            self.percent_changes.append(PercentChange())
        self.percent_changes[-1].set(v)

    def compute_net_percent_change(self):
        net = 0
        for percent_change in self.percent_changes:
            if percent_change.is_complete():
                net += percent_change.compute_change()
        return net


class Strategy(Subscribable):
    def __init__(self, proxy, conn, action):
        Subscribable.__init__(self)
        self.add_listener(proxy)
        self.dates = [
            date
            for date in range(action.start, action.end + action.period, action.period)
        ]
        self.idx = 0
        self.conn = conn
        self.exchange = action.exchange
        self.period = action.period
        self.pair = action.pair
        self.accumulator = Accumulator()
        self.last_avg_price = None
        self.is_locked = False
        ExchangeDatabase().register_chart_data(
            action.exchange, action.pair, action.period, action.start, action.end
        )

    def new_order(self):
        if not self.is_locked and self.last_avg_price is not None:
            self.accumulator.set(self.last_avg_price)
            self.is_locked = True

    def tick(self):
        if self.idx == len(self.dates) - 1:
            percent_change = self.accumulator.compute_net_percent_change()
            msg = json.dumps(
                {
                    "eventType": "END_OF_CHART_DATA",
                    "payload": {"percentChange": percent_change},
                }
            )
            self.conn.socket.send(msg.encode())
            self.notify_listeners(
                ActionFactory.instantiate(str(self.conn), msg), self.conn
            )
            return
        data = ExchangeDatabase().get_chart_data(
            self.exchange, self.pair, self.period, self.dates[self.idx]
        )
        if data is not None:
            self.is_locked = False
            high, low, open, close, weighted_average = data
            self.last_avg_price = weighted_average
            self.conn.socket.send(
                json.dumps(
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
                json.dumps(
                    {"eventType": "ERROR_CHART_DATA_DOES_NOT_EXIST", "payload": ""}
                ).encode()
            )
        self.idx += 1
