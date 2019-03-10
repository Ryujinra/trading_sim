import threading
import socket
import json
import os

from .subscribable import Handler
from .strategy import Strategy
from .event import Event, EventType
from util.logger import logger
from exchange.exchange_db import ExchangeDatabase


class Connection(object):

    def __init__(self, socket, addr):
        self.socket = socket
        self.addr = addr

    def get_conn(self):
        return (self.socket, self.addr)

    def __str__(self):
        ip, port = self.addr
        return 'from: {}:{}'.format(ip, port)

    def __repr__(self):
        return self.__str__()


class Proxy(Handler):

    HOST = 'localhost'
    PORT = 5000
    BUFFER_SIZE = 1024

    def __init__(self):
        self.strategies = {}
        self.exchange_db = ExchangeDatabase()
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.bind((self.HOST, self.PORT))
        logger.info('Listening...')
        while True:
            proxy.listen()
            _socket, addr = proxy.accept()
            conn = Connection(_socket, addr)
            logger.info('New connection {}'.format(conn))
            threading.Thread(target=self.listener, args=(conn,)).start()

    def get_db(self):
        return self.exchange_db

    def listener(self, conn):
        socket, addr = conn.get_conn()
        while True:
            msg = socket.recv(self.BUFFER_SIZE)
            try:
                msg = json.loads(msg)
            except ValueError:
                logger.info('Message {}: is not parsable to json'.format(conn))
                continue
            if all(key in msg for key in ('type', 'payload')):
                self.handler(Event(msg['type'], msg['payload'], conn))
            else:
                logger.info('Message {}: does not contain a type or payload'.format(conn))

    def handler(self, event):
        msg = event.to_json()
        conn = event.get_conn()
        logger.info('Message type: {}: {}'.format(msg['type'], conn))
        if msg['type'] == EventType.REGISTER_TEST_STRATEGY.name:
            if conn.get_conn() in self.strategies:
                logger.info('Strategy already exist {}: overriding the current strategy'.format(conn))
                self.strategies[conn.get_conn()].running = False
            self.strategies[conn.get_conn()] = Strategy(self, conn, msg['payload'])
            self.strategies[conn.get_conn()].start()
        elif msg['type'] == EventType.NEW_TEST_CANDLESTICK.name:
            if conn.get_conn() not in self.strategies:
                logger.info("Connection {}: is not a registered strategy".format(conn))
                return
            payload = msg['payload']
            high, low, open, close = self.exchange_db.get_chart_data(payload['exchange'], payload['pair'], payload['period'], payload['date'])
            socket, addr = conn.get_conn()
            data = {'high': high, 'low': low, 'open': open, 'close': close}
            socket.send(str(data).encode())
        else:
            logger.info('Invalid message type: {}: {}'.format(msg['type'], conn))
