from .action import Action
from util.logger import logger


class ActionTick(Action):
    def __init__(self):
        Action.__init__(self, None)
        self.action_type = self
