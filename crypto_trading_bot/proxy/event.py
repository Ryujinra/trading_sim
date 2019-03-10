import json

from enum import Enum


class EventType(Enum):

    REGISTER_TEST_STRATEGY = 'REGISTER_TEST_STRATEGY'
    NEW_TEST_CANDLESTICK = 'NEW_TEST_CANDLESTICK'


class Event(object):

    def __init__(self, type, payload, conn):
        self.type = type
        self.payload = payload
        self.conn = conn

    def get_conn(self):
        return self.conn

    def to_json(self):
        return json.loads(json.dumps({'type': self.type, 'payload': self.payload}))
