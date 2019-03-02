import logging
import threading
import os
import json
import socket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s::%(name)s:%(funcName)s:%(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Handler(object):

    def handler(self, event):
        pass


class Proxy(Handler):

    HOST = 'localhost'
    PORT = 5001
    BUFFER_SIZE = 1024

    def __init__(self):
        self.strategies = {}
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.bind((self.HOST, self.PORT))
        while True:
            proxy.listen()
            conn, addr = proxy.accept()
            threading.Thread(target=self.listener, args=(conn, addr)).start()

    def listener(self, conn, addr):
        while True:
            data = conn.recv(self.BUFFER_SIZE)
            try:
                data = json.loads(data)
            except ValueError:
                continue
            if "type" and "payload" in data:
                logger.info(data)
                self.handler(
                    Event(data['type'], data['payload'], conn, addr))

    def handler(self, event):
        if not isinstance(event, Event):
            return
        action = event.to_json()
        conn, addr = event.get_conn_and_addr()
        logger.info(action['type'])
        if action['type'] == 'REGISTER_STRATEGY':
            if (conn, addr) in self.strategies:
                logger.info(
                    "Connection already exist: {}: instantiating new "
                    "strategy".format(conn.getpeername()))
            self.strategies[(conn, addr)] = Strategy(self, conn, addr)
        elif action['type'] == 'NEW_CANDLESTICK':
            pass


class Event(object):

    def __init__(self, type, payload, conn, addr):
        self.type = type
        self.payload = payload
        self.conn = conn
        self.addr = addr

    def get_conn_and_addr(self):
        return (self.conn, self.addr)

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

    def __init__(self, interval=1):
        Subscribable.__init__(self)
        self.interval = interval

    def tick(self, event):
        self.notify_subscribers(event)
        threading.Timer(self.interval, self.tick, [event]).start()


class Strategy(Ticker):

    def __init__(self, proxy, conn, addr, interval=1):
        Ticker.__init__(self)
        self.add_subscriber(proxy)
        self.tick(Event('NEW_CANDLESTICK', '', conn, addr))


if __name__ == '__main__':
    Proxy()
