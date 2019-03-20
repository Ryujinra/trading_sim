from .action import Action


class ActionNewChartData(Action):
    def __init__(self, payload):
        Action.__init__(self)
        candlestick = payload["candlestick"]
        self.data = (
            candlestick["high"],
            candlestick["low"],
            candlestick["open"],
            candlestick["close"],
            candlestick["weightedAverage"],
            candlestick["volume"],
        )
        self.action_type = self
