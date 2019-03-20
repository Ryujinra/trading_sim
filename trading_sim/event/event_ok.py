import json

from .event_type import EventType


class EventOk:
    @staticmethod
    def instantiate():
        return json.dumps({"eventType": EventType.OK.value, "payload": {}}).encode()
