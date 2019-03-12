import time

from .action import Action
from exchange.exchange_db import ExchangeDatabase
from util.logger import logger


class ActionRegisterTestStrategy(Action):
    def __init__(self, payload):
        Action.__init__(self, payload)
        if any(
            key not in self.payload
            for key in ("exchange", "pair", "period", "start", "end")
        ):
            logger.debug("Event does not contain exchange, pair, period, start or end")
            return
        if not ExchangeDatabase().is_valid_exchange(self.payload["exchange"]):
            logger.debug("{}: is an invalid exchange".format(self.payload["exchange"]))
            return
        else:
            self.exchange = self.payload["exchange"]
        if not ExchangeDatabase().is_valid_currency_pair(
            self.payload["exchange"], self.payload["pair"]
        ):
            logger.debug("{}: is an invalid curreny pair".format(self.payload["pair"]))
            return
        else:
            self.pair = self.payload["pair"]
        if self.payload["period"] not in [300, 900, 1800, 7200, 14400, 86400]:
            logger.debug("{}: is an invalid period".format(self.payload["period"]))
            return
        else:
            self.period = self.payload["period"]
        if (
            self.payload["start"] % self.period != 0
            or self.payload["start"] < 0
            or self.payload["start"] > int(time.time())
        ):
            logger.debug("{}: is an invalid start window".format(self.payload["start"]))
            return
        else:
            self.start = self.payload["start"]
        if (
            self.payload["end"] % self.period != 0
            or self.payload["end"] < self.payload["start"]
            or self.payload["end"] > int(time.time())
        ):
            logger.debug("{}: is an invalid end window".format(self.payload["end"]))
            return
        else:
            self.end = self.payload["end"]
        self.action_type = self
