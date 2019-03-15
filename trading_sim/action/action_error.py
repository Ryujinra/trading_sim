import time

from .action import Action


class ActionError(Action):
    def __init__(self, payload):
        Action.__init__(self)
        self.error_type = payload["errorType"]
        self.action_type = self
