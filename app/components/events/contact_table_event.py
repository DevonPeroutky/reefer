from app.components.application.contact_table import ContactTable
from app.components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from app.actions import TaskStatus
from fasthtml.common import *
from app import Company, Contact, JobOpening
from typing import List, Tuple


class ContactTableEvent:
    def __init__(
        self,
        id: str,
        company: Company,
        job_contacts: List[Tuple[JobOpening, Contact]],
        hidden: bool = False,
        **kwargs,
    ):
        self.company = company
        self.status = TaskStatus.IN_PROGRESS
        self.hidden = hidden
        self.id = id
        self.kwargs = kwargs
        self.job_contacts = job_contacts

    def complete_task(self, job_contacts: List[Tuple[JobOpening, Contact]]):
        self.status = TaskStatus.COMPLETED
        self.job_contacts = job_contacts

    def __ft__(self):
        return Li(
            TimelineEventStatusIndicator(self.status, self.id),
            Div(
                ContactTable(company=self.company, job_contacts=self.job_contacts),
                cls="w-full py-4 px-6 flex flex-col gap-y-3 bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-700 dark:border-gray-600",
            ),
            cls=f"ms-6 flex items-start flex-col pl-2 {'hidden' if self.hidden else ''}",
            id=f"item-{self.id}",
            **self.kwargs,
            **{"hx_swap_oob": "true"} if self.status == TaskStatus.COMPLETED else {},
        )
