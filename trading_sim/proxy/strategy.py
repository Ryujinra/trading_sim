import math
import json

from util.util import Util
from util.logger import logger
from exchange.exchange_database import ExchangeDatabase
from action.action_factory import ActionFactory
from event.event_new_chart_data import EventNewChartData
from event.event_end_of_chart_data import EventEndOfChartData
from action.action_factory import ActionFactory
from action.action_limit_order import ActionLimitOrder
from action.action_tick import ActionTick
from action.action_end_of_chart_data import ActionEndOfChartData
from event.event_ok import EventOk


class PercentChange(object):
    def __init__(self):
        self.v1 = None
        self.v2 = None

    def is_complete(self):
        return self.v1 is not None and self.v2 is not None

    def compute_percent_change(self):
        if self.is_complete():
            percent_change = ((self.v2 - self.v1) * 100) / math.fabs(self.v1)
            logger.debug(
                "v1: {:.5f}, v2: {:.5f}, Δ%: {:.5f}".format(
                    self.v1, self.v2, percent_change
                )
            )
            return percent_change
        return 0


class PercentChangeAccumulator(object):
    def __init__(self):
        self.percent_changes = []
        self.sell_counter = 0

    def buy(self, v):
        self.percent_changes.append(PercentChange())
        self.percent_changes[-1].v1 = v
        logger.debug("Successfully registered a new buy order")

    def sell(self, v):
        # Ignore the sell order if there exist no existing buy orders.
        if not self.percent_changes or self.sell_counter == len(self.percent_changes):
            logger.debug(
                "Failed to register a new sell order because there exist no open buy orders"
            )
            return
        # Register the sell order and increment the sell order count.
        self.percent_changes[self.sell_counter].v2 = v
        self.sell_counter += 1
        logger.debug("Successfully registered a new sell order")

    def compute_net_percent_change(self):
        logger.debug("Computing the net percent change")
        net = 0
        for percent_change in self.percent_changes:
            net += percent_change.compute_percent_change()
        logger.debug("Net Δ%: {:.5f}".format(net))
        return net


class Strategy(object):
    def __init__(self, conn, addr, action):
        logger.debug("Instantiating a new test strategy")
        # Whether this strategy is actively listening and handling requests.
        self.is_running = True
        # Maintain a socket connection with the client.
        self.conn = conn
        self.addr = addr
        # The percent_change_accumulator field stores the history of limit
        # orders made to this strategy.
        self.percent_change_accumulator = PercentChangeAccumulator()
        # The is_locked variable prevents this test strategy from making
        # multiple limit orders for the same candlestick.  It is initially set
        # to True because a test strategy should not make a limit order until it
        # requests for the first candlestick.
        self.is_locked = True
        # Register the chart data required by this test strategy.
        ExchangeDatabase().register_chart_data(
            action.exchange, action.pair, action.period, action.start, action.end
        )
        # Collect the chart data required by this test strategy into an iterator
        # object.
        chart_data = []
        for date in range(action.start, action.end + action.period, action.period):
            data = ExchangeDatabase().get_chart_data(
                action.exchange, action.pair, action.period, date
            )
            # The chart data may not exist even after registering because the
            # data from the requested exchange may not exist for a given date.
            if data is not None:
                chart_data.append(data)
        self.chart_data_iter = iter(chart_data)
        # The curr_chart_data variable stores the state of the current chart
        # data referenced by the chart data iterator.
        self.curr_chart_data = None
        logger.debug("Sending ok")
        self.conn.send(EventOk.instantiate())
        # Start listening for requests.
        self.listener()

    def new_limit_order(self, action):
        # Register the limit order if and only if this strategy is not locked.
        if not self.is_locked:
            # Make the limit order using the weighted average of the current
            # candlestick.
            weighted_average = self.curr_chart_data[4]
            if action.is_buy_order:
                logger.debug(
                    "Registering a new buy order at price: {:.5f}".format(
                        weighted_average
                    )
                )
                self.percent_change_accumulator.buy(weighted_average)
            else:
                logger.debug(
                    "Registering a new sell order at price: {:.5f}".format(
                        weighted_average
                    )
                )
                self.percent_change_accumulator.sell(weighted_average)
            # Lock this strategy from making more limit orders until it
            # requests for the next candlestick.
            self.is_locked = True
        else:
            logger.debug("Strategy is blocked from making a new limit order")
        self.conn.send(EventOk.instantiate())

    def tick(self):
        try:
            self.curr_chart_data = next(self.chart_data_iter)
        except StopIteration:
            logger.debug(
                "End of the chart data: notifying the client and all listeners"
            )
            # If there is exist no more chart data, then send the client and
            # all listeners the performance metrics of this strategy.
            percent_change = (
                self.percent_change_accumulator.compute_net_percent_change()
            )
            self.conn.send(EventEndOfChartData.instantiate(percent_change))
            self.is_running = False
        else:
            logger.debug("Sending the chart data to the client")
            # If there still exist chart data, then unlock this strategy to
            # receive a limit order and send the chart data to the client.
            self.is_locked = False
            high, low, open, close, weightedAverage = self.curr_chart_data
            self.conn.send(
                EventNewChartData.instantiate(high, low, open, close, weightedAverage)
            )

    def listener(self):
        while self.is_running:
            logger.info("Listening...")
            data = self.conn.recv(Util.BUFFER_SIZE)
            self.reducer(ActionFactory.instantiate(data))

    def reducer(self, action):
        if isinstance(action, ActionLimitOrder):
            self.new_limit_order(action)
        elif isinstance(action, ActionTick):
            self.tick()
        else:
            logger.debug("Unexpected action: {}".format(action))
            self.is_running = False
