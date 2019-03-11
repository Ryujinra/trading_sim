from enum import Enum

from .action_register_test_strategy import ActionRegisterTestStrategy
from util.logger import logger


class EventType(Enum):

    REGISTER_TEST_STRATEGY = "REGISTER_TEST_STRATEGY"


class ActionFactory(object):
    @staticmethod
    def instantiate(addr, msg):
        if any(key not in msg for key in ("type", "payload")):
            logger.debug("Event does not contain a type or payload")
            return None
        logger.info("New message: {}: {}".format(addr, msg["type"]))
        return {
            EventType.REGISTER_TEST_STRATEGY.value: lambda: ActionRegisterTestStrategy(
                msg["payload"]
            )
        }[msg["type"]]().type
