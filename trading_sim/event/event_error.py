import json

from .event_type import EventType


class EventError:
    @staticmethod
    def instantiate(errorType):
        return json.dumps(
            {"eventType": EventType.ERROR.value, "payload": {"errorType": errorType}}
        ).encode()
