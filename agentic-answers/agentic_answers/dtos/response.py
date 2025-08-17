from typing import TypedDict


class EventData(TypedDict):
    content: str

class EventResponse(TypedDict):
    type: str
    data: EventData