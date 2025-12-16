from dataclasses import dataclass
import queue

class Event:
    """Base class for all events."""
    pass

@dataclass
class ButtonPressed(Event):
    button_id: int

@dataclass
class ButtonReleased(Event):
    button_id: int

class EventBus:
    def __init__(self):
        self._queue = queue.Queue()
        self._handlers = {}

    def post(self, event: Event):
        self._queue.put(event)

    def register(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch_all(self):
        while not self._queue.empty():
            event = self._queue.get()
            for handler in self._handlers.get(type(event), []):
                handler(event)
