import threading
import socket
import os
from concurrent.futures import ThreadPoolExecutor

from .strategy import Strategy
from util.logger import logger
from exchange.exchange_db import ExchangeDatabase
from .action.action_factory import ActionFactory
from .action.action_register_test_strategy import ActionRegisterTestStrategy
from .action.action_limit_order import ActionLimitOrder
from .action.action_tick import ActionTick


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
    PORT = 5000
    BUFFER_SIZE = 1024

    def __init__(self):
        self.strategies = {}
        self.thread_pool = ThreadPoolExecutor()
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.bind((self.HOST, self.PORT))
        logger.info("Listening...")
        while True:
            proxy.listen()
            _socket, addr = proxy.accept()
            conn = Connection(_socket, addr)
            logger.info("New connection {}".format(conn))
            self.thread_pool.submit(lambda: self.listener(conn))

    def listener(self, conn):
        while True:
            self.handler(
                ActionFactory.instantiate(
                    str(conn), conn.socket.recv(self.BUFFER_SIZE)
                ),
                conn,
            )

    def handler(self, action, conn):
        key = (conn.socket, conn.addr)
        if isinstance(action, ActionRegisterTestStrategy):
            if key in self.strategies:
                logger.debug(
                    "Strategy already exist {}: overriding the current strategy".format(
                        conn
                    )
                )
            self.strategies[key] = Strategy(
                conn,
                action.exchange,
                action.pair,
                action.period,
                action.start,
                action.end,
            )
        elif isinstance(action, ActionLimitOrder):
            if key not in self.strategies:
                logger.debug("Strategy does not exist {}".format(conn))
                return
            # TODO: Add handler.
        elif isinstance(action, ActionTick):
            if key not in self.strategies:
                logger.debug("Strategy does not exist {}".format(conn))
                return
            self.strategies[key].tick()
        else:
            logger.debug("Invalid message {}".format(conn))
