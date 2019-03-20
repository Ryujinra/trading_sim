from util.util import Util
from .bookkeeper import Bookkeeper


class Dispatcher:
    def __init__(self, strategies):
        # Bookkeeper shared amongst all strategies.
        self.bookkeeper = Bookkeeper()
        self.active = []
        # Instantiate Util.MAX_STRATEGIES strategies and place them into a
        # active list.
        for strategy in strategies[: Util.MAX_STRATEGIES]:
            strategy = strategy()
            strategy.add_listener(self.bookkeeper)
            self.active.append(strategy)
        # Place the remaining strategies in a passive list.
        self.passive = strategies[Util.MAX_STRATEGIES :]
        self.ptr = 0
        # Start all threads in the active list.
        for strategy in self.active:
            strategy.start()
        # Loop until a StopIteration is raised.
        for _ in self:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        # If there are no more active threads, then raise a StopIteration.
        if not self.active:
            self.bookkeeper.log()
            raise StopIteration()
        # If the thread pointed to by self.ptr is active check the succeeding
        # thread.
        if self.active[self.ptr % len(self.active)].isAlive():
            self.ptr += 1
        else:
            # Else, remove the dead thread from the active list.
            ptr = self.ptr % len(self.active)
            self.active.pop(ptr)
            if self.passive:
                # If there exists a passive strategy, then instantiate it and
                # insert it into the active list.
                strategy = self.passive.pop()()
                strategy.add_listener(self.bookkeeper)
                self.active.insert(ptr, strategy)
                self.active[ptr].start()
