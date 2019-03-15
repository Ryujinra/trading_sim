from .action import Action


class ActionEndOfChartData(Action):
    def __init__(self, payload):
        Action.__init__(self)
        self.percent_change = payload["percentChange"]
        self.action_type = self
