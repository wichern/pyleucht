from dataclasses import dataclass

class Event:
    """Base class for all events."""
    pass

@dataclass
class ButtonPressed(Event):
    button_id: int

@dataclass
class ButtonReleased(Event):
    button_id: int

