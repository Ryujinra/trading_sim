import json

from enum import Enum


class EventType(Enum):

    REGISTER_STRATEGY = 'REGISTER_STRATEGY'
    NEW_CANDLESTICK = 'NEW_CANDLESTICK'


class Event(object):

    def __init__(self, type, payload, conn, addr):
        self.type = type
        self.payload = payload
        self.conn = conn
        self.addr = addr

    def get_conn_and_addr(self):
        return (self.conn, self.addr)

    def to_json(self):
        return json.loads(json.dumps({
            'type': self.type,
            'payload': self.payload}))
