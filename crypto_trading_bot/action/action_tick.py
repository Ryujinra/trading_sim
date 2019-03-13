from .action import Action


class ActionTick(Action):
    def __init__(self):
        Action.__init__(self, None)
        self.action_type = self
