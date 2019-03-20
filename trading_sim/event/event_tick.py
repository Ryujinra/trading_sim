import json

from .event_type import EventType


class EventTick:
    @staticmethod
    def instantiate():
        return json.dumps({"eventType": EventType.TICK.value, "payload": {}}).encode()
