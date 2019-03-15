import time

from .action import Action
from exchange.exchange_database import ExchangeDatabase
from util.logger import logger


class ActionRegisterTestStrategy(Action):
    def __init__(self, payload):
        Action.__init__(self)
        if any(
            key not in payload for key in ("exchange", "pair", "period", "start", "end")
        ):
            logger.debug("Event does not contain exchange, pair, period, start or end")
            return
        if not ExchangeDatabase().is_valid_exchange(payload["exchange"]):
            logger.debug("{}: is an invalid exchange".format(payload["exchange"]))
            return
        else:
            self.exchange = payload["exchange"]
        if not ExchangeDatabase().is_valid_currency_pair(
            payload["exchange"], payload["pair"]
        ):
            logger.debug("{}: is an invalid curreny pair".format(payload["pair"]))
            return
        else:
            self.pair = payload["pair"]
        if payload["period"] not in [300, 900, 1800, 7200, 14400, 86400]:
            logger.debug("{}: is an invalid period".format(payload["period"]))
            return
        else:
            self.period = payload["period"]
        if (
            payload["start"] % self.period != 0
            or payload["start"] < 0
            or payload["start"] > int(time.time())
        ):
            logger.debug("{}: is an invalid start window".format(payload["start"]))
            return
        else:
            self.start = payload["start"]
        if (
            payload["end"] % self.period != 0
            or payload["end"] < payload["start"]
            or payload["end"] > int(time.time())
        ):
            logger.debug("{}: is an invalid end window".format(payload["end"]))
            return
        else:
            self.end = payload["end"]
        self.action_type = self
