import json

from .event_type import EventType


class EventTick(object):
    @staticmethod
    def instantiate():
        return json.dumps({"eventType": EventType.TICK.value, "payload": {}}).encode()
