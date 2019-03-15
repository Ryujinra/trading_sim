import json

from .event_type import EventType


class EventNewChartData(object):
    @staticmethod
    def instantiate(high, low, open, close, weighted_average):
        return json.dumps(
            {
                "eventType": EventType.NEW_CHART_DATA.value,
                "payload": {
                    "candlestick": {
                        "high": high,
                        "low": low,
                        "open": open,
                        "close": close,
                        "weightedAverage": weighted_average,
                    }
                },
            }
        ).encode()
