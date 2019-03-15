import json

from .event_type import EventType


class EventRegisterTestStrategy(object):
    @staticmethod
    def instantiate(exchange, pair, period, start, end):
        return json.dumps(
            {
                "eventType": EventType.REGISTER_TEST_STRATEGY.value,
                "payload": {
                    "exchange": exchange,
                    "pair": pair,
                    "period": period,
                    "start": start,
                    "end": end,
                },
            }
        ).encode()
