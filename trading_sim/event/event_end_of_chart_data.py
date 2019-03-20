import json

from .event_type import EventType


class EventEndOfChartData:
    @staticmethod
    def instantiate(percent_change, trades_made):
        return json.dumps(
            {
                "eventType": EventType.END_OF_CHART_DATA.value,
                "payload": {"percentChange": percent_change, "tradesMade": trades_made},
            }
        ).encode()
