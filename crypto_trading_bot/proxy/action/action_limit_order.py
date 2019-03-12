from .action import Action
from util.logger import logger


class ActionLimitOrder(Action):
    def __init__(self, payload):
        Action.__init__(self, payload)
        if "orderType" not in payload:
            logger.debug("Event does not contain an order type")
            return
        if payload["orderType"] not in ["BUY", "SELL"]:
            logger.debug(
                "{}: is an invalid order type".format(self.payload["orderType"])
            )
            return
        self.order_type = self.payload["orderType"]
        self.action_type = self
