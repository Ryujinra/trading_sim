import threading
import socket
import json
import os
from concurrent.futures import ThreadPoolExecutor

from .strategy import Strategy
from util.logger import logger
from exchange.exchange_db import ExchangeDatabase
from .action.action_factory import ActionFactory
from .action.action_register_test_strategy import ActionRegisterTestStrategy


class Connection(object):
    def __init__(self, socket, addr):
        self.socket = socket
        self.addr = addr

    def __str__(self):
        ip, port = self.addr
        return "from: {}:{}".format(ip, port)

    def __repr__(self):
        return self.__str__()


class Proxy(object):

    HOST = "localhost"
    PORT = 5001
    BUFFER_SIZE = 1024

    def __init__(self):
        self.strategies = {}
        self.executor = ThreadPoolExecutor()
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.bind((self.HOST, self.PORT))
        logger.info("Listening...")
        while True:
            proxy.listen()
            _socket, addr = proxy.accept()
            conn = Connection(_socket, addr)
            logger.info("New connection {}".format(conn))
            threading.Thread(target=self.listener, args=(conn,)).start()

    def listener(self, conn):
        while True:
            msg = conn.socket.recv(self.BUFFER_SIZE)
            try:
                msg = json.loads(msg)
            except ValueError:
                logger.debug("Message {}: is not parsable to json".format(conn))
                continue
            self.executor.submit(
                lambda: self.handler(ActionFactory.instantiate(str(conn), msg), conn)
            )

    def handler(self, action, conn):
        if isinstance(action, ActionRegisterTestStrategy):
            key = (conn.socket, conn.addr)
            if key in self.strategies:
                logger.debug(
                    "Strategy already exist {}: overriding the current strategy".format(
                        conn
                    )
                )
                self.strategies[key].running = False
            self.strategies[key] = Strategy(
                conn,
                action.exchange,
                action.pair,
                action.period,
                action.start,
                action.end,
            )
        else:
            logger.debug("Invalid message {}".format(conn))
