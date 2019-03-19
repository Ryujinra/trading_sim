import socket

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
    # A wrapper function that awaits an ok message from the proxy server.
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        data = args[0]._socket.recv(Util.BUFFER_SIZE)
        action = ActionFactory.instantiate(data)
        if isinstance(action, ActionError):
            raise Exception(action.error_type)
        if not isinstance(action, ActionOk):
            raise Exception("Unexpected action: {}".format(action))

    return wrapper


class Strategy:
    def __init__(self, exchange, pair, period, start, end):
        # Instantiate the socket and bind to the proxy address.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((Util.PROXY_HOST, Util.PROXY_PORT))
        # Register the strategy with the proxy server.
        self._register_test_strategy(exchange, pair, period, start, end)

    @await_ok
    def _register_test_strategy(self, exchange, pair, period, start, end):
        self._socket.send(
            EventRegisterTestStrategy.instantiate(exchange, pair, period, start, end)
        )

    @await_ok
    def new_buy_order(self):
        self._socket.send(EventBuy.instantiate())

    @await_ok
    def new_sell_order(self):
        self._socket.send(EventSell.instantiate())

    def __iter__(self):
        return self

    def __next__(self):
        # Send tick event to the proxy server and await a response.
        self._socket.send(EventTick.instantiate())
        buf = self._socket.recv(Util.BUFFER_SIZE)
        action = ActionFactory.instantiate(buf)
        if isinstance(action, ActionNewChartData):
            return action.data
        self._socket.close()
        if isinstance(action, ActionEndOfChartData):
            raise StopIteration()
        elif isinstance(action, ActionError):
            raise Exception(action.error_type)
        else:
            raise Exception("Unexpected action: {}".format(action))
