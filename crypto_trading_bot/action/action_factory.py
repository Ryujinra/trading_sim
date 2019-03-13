from enum import Enum
import json

from .action_register_test_strategy import ActionRegisterTestStrategy
from .action_limit_order import ActionLimitOrder
from .action_tick import ActionTick
from .action_end_of_chart_data import ActionEndOfChartData
from util.logger import logger


class EventType(Enum):

    REGISTER_TEST_STRATEGY = "REGISTER_TEST_STRATEGY"
    LIMIT_ORDER = "LIMIT_ORDER"
    TICK = "TICK"
    END_OF_CHART_DATA = "END_OF_CHART_DATA"


class ActionFactory(object):
    @staticmethod
    def instantiate(addr, msg):
        try:
            msg = json.loads(msg)
        except ValueError:
            logger.debug("Message {}: is not parsable to json".format(addr))
            return None
        if any(key not in msg for key in ("eventType", "payload")):
            logger.debug("Event does not contain an event type or payload")
            return None
        logger.info("New message: {}: {}".format(msg["eventType"], addr))
        return {
            EventType.REGISTER_TEST_STRATEGY.value: lambda: ActionRegisterTestStrategy(
                msg["payload"]
            ),
            EventType.LIMIT_ORDER.value: lambda: ActionLimitOrder(msg["payload"]),
            EventType.TICK.value: lambda: ActionTick(),
            EventType.END_OF_CHART_DATA.value: lambda: ActionEndOfChartData(),
        }[msg["eventType"]]().action_type
