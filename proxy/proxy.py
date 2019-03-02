import logging
import threading
import socket
import json

from subscribable import Handler
from strategy import Strategy
from event import Event, EventType

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
            ip, port = addr
            logger.info('New connection: {}:{}'.format(ip, port))
            threading.Thread(target=self.listener, args=(conn, addr)).start()

    def listener(self, conn, addr):
        ip, port = addr
        while True:
            msg = conn.recv(self.BUFFER_SIZE)
            try:
                msg = json.loads(msg)
            except ValueError:
                logger.info('Message from: {}:{}: is not parsable to '
                            'json'.format(ip, port))
                continue
            if 'type' and 'payload' in msg:
                self.handler(
                    Event(msg['type'], msg['payload'], conn, addr))
            else:
                logger.info(
                    'Message from: {}:{}: does not contain type or '
                    'payload'.format(ip, port))

    def handler(self, event):
        msg = event.to_json()
        conn, addr = event.get_conn_and_addr()
        ip, port = addr
        logger.info('Message type: {}: from: {}:{}'.format(
            msg['type'], ip, port))
        if msg['type'] == EventType.REGISTER_STRATEGY:
            if ('exchange' and 'currencyPair' and 'amount'
                    not in msg['payload']):
                logger.info('{} : from {}:{}: does not contain exchange, '
                            'currency pair or amount'.format(
                                EventType.REGISTER_STRATEGY, ip, port))
                return
            if (conn, addr) in self.strategies:
                logger.info(
                    'Strategy already exist from: {}:{}: overriding the '
                    'current strategy'.format(ip, port))
                self.strategies[(conn, addr)].running = False
            self.strategies[(conn, addr)] = Strategy(self, conn, addr)
        elif msg['type'] == EventType.NEW_CANDLESTICK:
            pass
        else:
            logger.info('Invalid message type: {}: from: {}:{}'.format(
                msg['type'], ip, port))


if __name__ == '__main__':
    Proxy()
