from threading import Thread

from util.util import Util


class Dispatcher:
    def __init__(self, strategies):
        tStrategy = []
        # Convert all class functions to a Thread object.
        for strategy in strategies:
            tStrategy.append(Thread(target=strategy))
        # Set the number of active threads to Util.MAX_STRATEGIES
        self.active = tStrategy[: Util.MAX_STRATEGIES]
        # Start all threads in the active list.
        for strategy in self.active:
            strategy.start()
        # Place the remaining threads in a passive list.
        self.passive = tStrategy[Util.MAX_STRATEGIES :]
        self.ptr = 0
        # Loop until StopIteration
        for _ in self:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        # If there are no more active threads, then raise StopIteration
        if not self.active:
            raise StopIteration()
        # If the thread pointed to by self.ptr is active check the following
        # thread.
        if self.active[self.ptr % len(self.active)].isAlive():
            self.ptr += 1
        else:
            # Else, remove the dead thread from the active list.
            ptr = self.ptr % len(self.active)
            self.active.pop(ptr)
            if self.passive:
                # If there exists a passive thread, then insert into it into
                # the active list and start it.
                self.active.insert(ptr, self.passive.pop())
                self.active[ptr].start()
