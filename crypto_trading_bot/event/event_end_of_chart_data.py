import json

from .event_type import EventType


class EventEndOfChartData(object):
    @staticmethod
    def instantiate(percent_change):
        return json.dumps(
            {
                "eventType": EventType.END_OF_CHART_DATA.value,
                "payload": {"percentChange": percent_change},
            }
        ).encode()
