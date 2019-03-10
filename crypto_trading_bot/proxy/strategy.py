import threading

from .subscribable import Subscribable
from .event import Event, EventType
from util.logger import logger

class Strategy(Subscribable, threading.Thread):

    def __init__(self, proxy, conn, payload):
        Subscribable.__init__(self)
        threading.Thread.__init__(self)
        if any(key not in payload for key in ('exchange','pair', 'period', 'start', 'end')):
            logger.info('{}: {}: message does not contain exchange, pair, interval, start or end'.format(EventType.REGISTER_TEST_STRATEGY, conn))
            return
        if not proxy.get_db().is_valid_exchange(payload['exchange']):
            logger.info(
                "{}: {}: is an invalid exchange".format(payload['exchange'], conn))
            return
        if not proxy.get_db().is_valid_currency_pair(payload['exchange'], payload['pair']):
            logger.info(
                "{}: {}: is an invalid curreny pair".format(payload['pair'], conn))
            return
        if payload['period'] not in [300, 900, 1800, 7200, 14400, 86400]:
            logger.info("{}: {}: is an invalid period".format(payload['period'], conn))
            return
        # TODO: Check valid start and end time.
        self.exchange = payload['exchange']
        self.pair = payload['pair']
        self.period = payload['period']
        self._start = payload['start']
        self.end = payload['end']
        self.conn = conn
        proxy.get_db().register_chart_data(self.exchange, self.pair, self.period, self._start, self.end)
        self.add_subscriber(proxy)

    def run(self):
        for date in range(self._start, self.end + self.period, self.period):
            self.notify_subscribers(Event(EventType.NEW_TEST_CANDLESTICK.name, {'exchange': self.exchange, 'pair': self.pair, 'period': self.period, 'date': date}, self.conn))
