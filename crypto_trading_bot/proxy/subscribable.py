class Listener(object):
    def handler(self, action, conn):
        pass


class Subscribable(object):
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        if isinstance(listener, Listener):
            self.listeners.append(listener)

    def notify_listeners(self, action, conn):
        for listener in self.listeners:
            listener.handler(action, conn)
