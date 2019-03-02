from event import Event


class Handler(object):

    def handler(self, event):
        pass


class Subscribable(object):

    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        if isinstance(subscriber, Handler):
            self.subscribers.append(subscriber)

    def notify_subscribers(self, event):
        if not isinstance(event, Event):
            return
        for subscriber in self.subscribers:
            subscriber.handler(event)
