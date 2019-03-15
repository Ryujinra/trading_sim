import socket
import json
import threading
import time

from util.logger import logger
from util.util import Util
from event.event_register_test_strategy import EventRegisterTestStrategy
from event.event_tick import EventTick
from event.event_buy import EventBuy
from event.event_sell import EventSell
from action.action_factory import ActionFactory
from action.action_end_of_chart_data import ActionEndOfChartData
from action.action_error import ActionError
from action.action_new_chart_data import ActionNewChartData
from action.action_ok import ActionOk


def await_ok(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        data = args[0].socket.recv(Util.BUFFER_SIZE)
        action = ActionFactory.instantiate(data)
        if not isinstance(action, ActionOk):
            logger.fatal("Expected an ok message! got: {}".format(action))
            exit()

    return wrapper


class ProxyAPI(threading.Thread):
    def __init__(self, exchange, pair, period, start, end):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((Util.PROXY_HOST, Util.PROXY_PORT))
        self.percent_change = 0
        self.is_running = True
        self.register_test_strategy(exchange, pair, period, start, end)

    @await_ok
    def register_test_strategy(self, exchange, pair, period, start, end):
        self.socket.send(
            EventRegisterTestStrategy.instantiate(exchange, pair, period, start, end)
        )

    def tick(self):
        self.socket.send(EventTick.instantiate())

    @await_ok
    def buy_order(self):
        self.socket.send(EventBuy.instantiate())

    @await_ok
    def sell_order(self):
        self.socket.send(EventSell.instantiate())

    def run(self):
        while self.is_running:
            self.tick()
            data = self.socket.recv(Util.BUFFER_SIZE)
            self.handler(ActionFactory.instantiate(data))

    def handler(self, action):
        if isinstance(action, ActionNewChartData):
            self.strategy(
                action.high,
                action.low,
                action.open,
                action.close,
                action.weighted_average,
            )
        elif isinstance(action, ActionError):
            logger.fatal(action.error_type)
            self.is_running = False
        elif isinstance(action, ActionEndOfChartData):
            self.percent_change = action.percent_change
            self.is_running = False
        elif isinstance(acton, ActionOk):
            pass

    def strategy(self, high, low, open, close, weighted_average):
        pass
