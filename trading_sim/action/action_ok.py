from .action import Action


class ActionOk(Action):
    def __init__(self):
        Action.__init__(self)
        self.action_type = self
