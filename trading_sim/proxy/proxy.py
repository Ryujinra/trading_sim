import socket
from concurrent.futures import ThreadPoolExecutor

from .strategy import Strategy
from util.logger import logger
from util.util import Util
from action.action_factory import ActionFactory
from action.action_register_test_strategy import ActionRegisterTestStrategy
from event.event_error import EventError
from action.action_error import ActionError


class Proxy(object):
    def __init__(self):
        # Instantiate the thread pool with Util.MAX_STRATEGIES workers.
        self.thread_pool = ThreadPoolExecutor(max_workers=Util.MAX_STRATEGIES)
        # Instantiate the server socket.
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.bind((Util.PROXY_HOST, Util.PROXY_PORT))
        # Listen for connections...
        self.listener()

    def listener(self):
        while 1:
            logger.info("Proxy is listening...")
            self.proxy.listen(Util.MAX_STRATEGIES)
            conn, addr = self.proxy.accept()
            conn.settimeout(Util.TIMEOUT)
            # Submit the new connection to the thread pool.
            self.thread_pool.submit(lambda: self.handler(conn, addr))

    def handler(self, conn, addr):
        ip, port = addr
        logger.info("New connection: {}:{}".format(ip, port))
        try:
            data = conn.recv(Util.BUFFER_SIZE)
        except socket.timeout:
            logger.debug("Connection: {}:{}: timed out".format(ip, port))
            conn.close()
            return
        # Instantiate the action.
        action = ActionFactory.instantiate(data)
        # Handle the instantiated action.
        if isinstance(action, ActionRegisterTestStrategy):
            # Instantiate a new strategy.
            Strategy(conn, addr, action)
        elif isinstance(action, ActionError):
            # Notify connection of the error.
            conn.send(EventError.instantiate(action.error_type))
        # Close the connection after handling the request.
        conn.close()
