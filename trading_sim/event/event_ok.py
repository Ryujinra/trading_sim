import json

from .event_type import EventType


class EventOk(object):
    @staticmethod
    def instantiate():
        return json.dumps({"eventType": EventType.OK.value, "payload": {}}).encode()
