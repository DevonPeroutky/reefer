from typing import List, TypeVar
from fasthtml.common import Div, Ol

from app.components.events import ActionEvent
from app.components.primitives.modal import ModalButton


T = TypeVar("T", bound="ActionEvent")


class Timeline:
    def __init__(self, id: str, events: List[T], company_name: str):
        self.id = id
        self.events = events
        self.company_name = company_name

    def __ft__(self):
        return Ol(
            *self.events,
            # THIS DOES NOT REPLACE THE CONTENT OF THE MODEL
            ModalButton(
                text="View Details",
                hx_get=f"/modal?job_id={0}&contact_id={1}",
                data_modal_target="details-modal",
                data_modal_show="details-modal",
                hx_swap="innerHTML",
                hx_target="#details-modal-body",
                hx_trigger="click",
            ),
            id=self.id,
            hx_post=f"/stream_action_plan?company_name={self.company_name}",
            hx_trigger="load",
            # hx_target=f"#{self.id}",
            hx_swap="beforeend",
            # hx_swap="innerHTML",
            hx_ext="chunked-transfer",
            cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
        )
