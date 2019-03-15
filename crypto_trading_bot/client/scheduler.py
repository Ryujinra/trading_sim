from util.util import Util
from util.logger import logger


class Scheduler(object):
    def __init__(self, strategies):
        if len(strategies) > Util.MAX_STRATEGIES:
            logger.fatal(
                "Too many strategies: the proxy server can only handle {} concurrent strategies".format(
                    Util.MAX_STRATEGIES
                )
            )
            exit()
        self.strategies = []
        for strategy in strategies:
            self.strategies.append(strategy())
        self.dispatcher()

    def dispatcher(self):
        for strategy in self.strategies:
            strategy.start()
        for strategy in self.strategies:
            strategy.join()
        ranking = []
        for strategy in self.strategies:
            ranking.append((strategy.percent_change, strategy.__class__.__name__))
        ranking.sort()
        ranking.reverse()
        for percent_change, strategy_name in ranking:
            print("{}: {}%".format(strategy_name, percent_change))
