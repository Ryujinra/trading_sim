import threading
import socket
import os
import time
from concurrent.futures import ThreadPoolExecutor

from .strategy import Strategy
from util.logger import logger
from util.util import Util
from exchange.exchange_database import ExchangeDatabase
from action.action_factory import ActionFactory
from action.action_register_test_strategy import ActionRegisterTestStrategy
from event.event_error import EventError


class Proxy(object):
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=Util.MAX_STRATEGIES)
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.bind((Util.PROXY_HOST, Util.PROXY_PORT))
        self.listener()

    def listener(self):
        while 1:
            logger.info("Listening...")
            self.proxy.listen(Util.MAX_STRATEGIES)
            conn, addr = self.proxy.accept()
            self.thread_pool.submit(lambda: self.handler(conn, addr))

    def handler(self, conn, addr):
        ip, port = addr
        logger.info("New connection: {}:{}".format(ip, port))
        data = conn.recv(Util.BUFFER_SIZE)
        action = ActionFactory.instantiate(data)
        if isinstance(action, ActionRegisterTestStrategy):
            logger.info("Instantiating a new test strategy")
            Strategy(conn, addr, action)
        else:
            logger.info("Invalid instantiation of a test strategy: closing the socket")
            conn.send(
                EventError.instantiate("Invalid instantiation of a test strategy")
            )
        conn.close()
