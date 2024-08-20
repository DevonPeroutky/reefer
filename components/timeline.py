from typing import List, TypeVar
import fasthtml.svg as svg
from fasthtml.common import Div, Span, Li, H3, P, Ol

from data_types import ActionEvent, TaskStatus


T = TypeVar("T", bound="ActionEvent")


class Timeline:
    def __init__(self, id: str, events: List[T], company: str):
        self.id = id
        self.events = events
        self.company = company

    def __ft__(self):
        return Ol(
            *self.events,
            id=self.id,
            hx_post=f"/stream_action_plan?company={self.company}",
            hx_trigger="load",
            # hx_target=f"#{self.id}",
            hx_swap="beforeend",
            # hx_swap="innerHTML",
            hx_ext="chunked-transfer",
            cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
        )
