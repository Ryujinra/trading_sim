import json

from .event_type import EventType


class EventSell(object):
    @staticmethod
    def instantiate():
        return json.dumps(
            {"eventType": EventType.LIMIT_ORDER.value, "payload": {"orderType": "SELL"}}
        ).encode()
