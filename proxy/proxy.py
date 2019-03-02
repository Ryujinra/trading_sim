import logging
import threading
import socket
import json

from subscribable import Handler
from strategy import Strategy
from event import Event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Proxy(Handler):

    HOST = 'localhost'
    PORT = 5000
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
                ip, port = conn.getpeername()
                logger.info(
                    "Connection already exist: {}:{}: overriding the current strategy".format(ip, port))
                self.strategies[(conn, addr)].running = False
            self.strategies[(conn, addr)] = Strategy(self, conn, addr)
        elif action['type'] == 'NEW_CANDLESTICK':
            pass


if __name__ == '__main__':
    Proxy()
