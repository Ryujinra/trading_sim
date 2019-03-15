import time

from .action import Action


class ActionNewChartData(Action):
    def __init__(self, payload):
        Action.__init__(self)
        candlestick = payload["candlestick"]
        self.high = candlestick["high"]
        self.low = candlestick["low"]
        self.open = candlestick["open"]
        self.close = candlestick["close"]
        self.weighted_average = candlestick["weightedAverage"]
        self.action_type = self
