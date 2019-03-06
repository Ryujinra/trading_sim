import threading

from .subscribable import Subscribable
from .event import Event, EventType


class Ticker(Subscribable):

    def __init__(self, interval):
        Subscribable.__init__(self)
        self.interval = interval
        self.running = True

    def tick(self, event):
        if not self.running:
            return
        self.notify_subscribers(event)
        threading.Timer(self.interval, self.tick, [event]).start()


class Strategy(Ticker):

    def __init__(self, proxy, msg, conn, addr):
        Ticker.__init__(self, msg['interval'])
        self.currency_pair = msg['currencyPair']
        self.amount = msg['amount']
        self.exchange = msg['exchange']
        self.add_subscriber(proxy)
        self.tick(Event(EventType.NEW_CANDLESTICK.name, '', conn, addr))
