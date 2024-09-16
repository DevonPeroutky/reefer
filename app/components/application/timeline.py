from typing import List, TypeVar
from fasthtml.common import Div, Ol
from app.components.events.action_event import ActionEvent


T = TypeVar("T", bound="ActionEvent")


class Timeline:
    def __init__(self, id: str, company_name: str, events: List[T] = []):
        self.id = id
        self.events = events
        self.company_name = company_name

    def __ft__(self):
        return Ol(
            *self.events,
            id=self.id,
            cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
        )
