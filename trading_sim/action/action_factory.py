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
from event.event_error import EventError


class ActionFactory(object):
    @staticmethod
    def instantiate(event):
        try:
            event = json.loads((event.decode()))
        except ValueError:
            logger.debug("{} is not valid json".format(event))
            return ActionError(
                EventError.instantiate("{}: is not valid json".format(event))
            )
        if any(key not in event for key in ("eventType", "payload")):
            logger.debug("Event does not contain an event type or payload")
            return ActionError(
                EventError.instantiate(
                    "Event does not contain an event type or payload"
                )
            )
        logger.info("New message: {}".format(event["eventType"]))
        return {
            EventType.REGISTER_TEST_STRATEGY.value: lambda: ActionRegisterTestStrategy(
                event["payload"]
            ),
            EventType.LIMIT_ORDER.value: lambda: ActionLimitOrder(event["payload"]),
            EventType.TICK.value: lambda: ActionTick(),
            EventType.END_OF_CHART_DATA.value: lambda: ActionEndOfChartData(
                event["payload"]
            ),
            EventType.NEW_CHART_DATA.value: lambda: ActionNewChartData(
                event["payload"]
            ),
            EventType.ERROR.value: lambda: ActionError(event["payload"]),
            EventType.OK.value: lambda: ActionOk(),
        }[event["eventType"]]().action_type
