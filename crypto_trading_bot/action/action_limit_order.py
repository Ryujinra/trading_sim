from .action import Action
from util.logger import logger


class ActionLimitOrder(Action):
    def __init__(self, payload):
        Action.__init__(self)
        if "orderType" not in payload:
            logger.debug("Event does not contain an order type")
            return
        if payload["orderType"] not in ["BUY", "SELL"]:
            logger.debug("{}: is an invalid order type".format(payload["orderType"]))
            return
        if payload["orderType"] == "BUY":
            self.is_buy_order = True
        else:
            self.is_buy_order = False
        self.action_type = self
