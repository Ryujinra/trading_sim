import logging
import threading
import os
import json
import socket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Handler(object):

    def handler(self, event, tokens):
        pass


class Proxy(Handler):

    HOST = 'localhost'
    PORT = 5000

    def __init__(self):
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.bind((self.HOST, self.PORT))
        self.listener()

    def listener(self):
        while True:
            self.proxy.listen()
            conn, addr = self.proxy.accept()
            with conn:
                data = conn.recv(1024)
                try:
                    data = json.loads(data)
                except ValueError:
                    continue
                if "type" and "payload" in data:
                    logger.info(data)
                    self.handler(data)

    def handler(self, event):
        logger.info(event['type'])
        if event['type'] == 'REGISTER_STRATEGY':
            Strategy(self)
        elif event['type'] == 'NEW_CANDLESTICK':
            pass


class Event(object):

    def __init__(self, type, payload):
        self.type = type
        self.payload = payload

    def to_json(self):
        return json.loads(json.dumps({'type': self.type, 'payload': self.payload}))


class Subscribable(object):

    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        if isinstance(subscriber, Handler):
            self.subscribers.append(subscriber)

    def notify_subscribers(self, event):
        for subscriber in self.subscribers:
            subscriber.handler(event)


class Ticker(Subscribable):

    def __init__(self, interval):
        Subscribable.__init__(self)
        self.interval = interval

    def tick(self, event):
        self.notify_subscribers(event)
        threading.Timer(self.interval, self.tick, [event]).start()


class Strategy(Ticker):

    def __init__(self, proxy, interval=1):
        Ticker.__init__(self, interval)
        self.add_subscriber(proxy)
        self.tick(Event('NEW_CANDLESTICK', '').to_json())


if __name__ == '__main__':
    Proxy()
