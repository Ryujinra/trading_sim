import json

from .event_type import EventType


class EventBuy:
    @staticmethod
    def instantiate():
        return json.dumps(
            {"eventType": EventType.LIMIT_ORDER.value, "payload": {"orderType": "BUY"}}
        ).encode()
