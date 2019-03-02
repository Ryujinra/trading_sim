import threading

from subscribable import Subscribable
from event import Event


class Ticker(Subscribable):

    def __init__(self, interval=1):
        Subscribable.__init__(self)
        self.interval = interval
        self.running = True

    def tick(self, event):
        if not self.running:
            return
        self.notify_subscribers(event)
        threading.Timer(self.interval, self.tick, [event]).start()


class Strategy(Ticker):

    def __init__(self, proxy, conn, addr, interval=1):
        Ticker.__init__(self)
        self.add_subscriber(proxy)
        self.tick(Event('NEW_CANDLESTICK', '', conn, addr))
