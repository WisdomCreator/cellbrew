from collections import defaultdict
from typing import Any, Callable, DefaultDict

EventHandler = Callable[..., None]


class EventBus:
    def __init__(self):
        self.__subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler):
        handlers = self.__subscribers[event_name]
        if handler in handlers:
            raise ValueError(f"Handler {handler} is already subscribed to {event_name}")
        handlers.append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler):
        handlers = self.__subscribers.get(event_name)
        if not handlers:
            raise ValueError(f"Event {event_name} does not exist")
        if handler in handlers:
            handlers.remove(handler)
        else:
            raise ValueError(f"Handler {handler} is not subscribed to {event_name}")

    def emit(self, event_name: str, /, *args: Any, **kwargs: Any):
        for handler in tuple(self.__subscribers[event_name]):
            handler(*args, **kwargs)
