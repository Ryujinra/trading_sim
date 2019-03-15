import json

from .action_register_test_strategy import ActionRegisterTestStrategy
from .action_limit_order import ActionLimitOrder
from .action_tick import ActionTick
from .action_end_of_chart_data import ActionEndOfChartData
from .action_error import ActionError
from .action_new_chart_data import ActionNewChartData
from util.logger import logger
from event.event_type import EventType
from .action_ok import ActionOk


class ActionFactory(object):
    @staticmethod
    def instantiate(msg):
        try:
            msg = json.loads((msg.decode()))
        except ValueError:
            logger.debug("Message is not valid json")
            return None
        if any(key not in msg for key in ("eventType", "payload")):
            logger.debug("Event does not contain an event type or payload")
            return None
        logger.info("New message: {}".format(msg["eventType"]))
        return {
            EventType.REGISTER_TEST_STRATEGY.value: lambda: ActionRegisterTestStrategy(
                msg["payload"]
            ),
            EventType.LIMIT_ORDER.value: lambda: ActionLimitOrder(msg["payload"]),
            EventType.TICK.value: lambda: ActionTick(),
            EventType.END_OF_CHART_DATA.value: lambda: ActionEndOfChartData(
                msg["payload"]
            ),
            EventType.NEW_CHART_DATA.value: lambda: ActionNewChartData(msg["payload"]),
            EventType.ERROR.value: lambda: ActionError(msg["payload"]),
            EventType.OK.value: lambda: ActionOk(),
        }[msg["eventType"]]().action_type
