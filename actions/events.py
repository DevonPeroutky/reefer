from abc import abstractmethod
import fasthtml.svg as svg
from itertools import groupby as itertools_groupby

from uuid import uuid4
from typing import List, Optional, TypeVar, Generic, AsyncGenerator, Tuple
from fasthtml.common import *

from components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from components.application.contact_table import ContactTable
from components.primitives.tag import (
    CompanyTag,
    JobTypeTag,
    OutputInputTag,
    PositionTag,
    KeywordTag,
)
from data_types import Company, Contact, JobOpening
from enums import TaskStatus, TaskType
from abc import ABC, abstractmethod


T = TypeVar("T")


class BaseAction(ABC, Generic[T]):
    @abstractmethod
    async def yield_action_stream(self, *args, **kwargs) -> AsyncGenerator[Safe, None]:
        pass

    @abstractmethod
    def yield_action_result(self) -> T:
        pass


class ActionEvent:
    def __init__(
        self,
        company_name: str,
        status: TaskStatus,
        task_type: TaskType,
        id: Optional[str] = None,
        **kwargs,
    ):
        self.id = str(id) if id is not None else str(uuid4())
        self.status = status
        self.task_type = task_type
        self.kwargs = kwargs
        self.company_name = company_name

    def _prepare_for_dom_update(self):
        self.kwargs["hx_swap_oob"] = "true"

    def complete_task(self, *args, **kwargs):
        self.status = TaskStatus.COMPLETED
        self._prepare_for_dom_update()

    @abstractmethod
    def _render_title(self):
        pass

    @abstractmethod
    def _render_details(self):
        pass

    def __ft__(self):
        details = (
            Div(
                Div(
                    self._render_details(),
                    cls="p-3 font-normal text-gray-500 border border-gray-200 rounded-lg bg-gray-50 dark:bg-gray-600 dark:border-gray-500 dark:text-gray-300",
                ),
            )
            if self._render_details()
            else None
        )

        return Li(
            TimelineEventStatusIndicator(self.status, self.id),
            Div(
                self._render_title(),
                details,
                cls="py-4 px-6 flex flex-col gap-y-3 bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-700 dark:border-gray-600",
            ),
            cls="ms-6 flex items-start flex-col pl-2",
            id=f"item-{self.id}",
            # sse_swap=f"sse-item-{self.id}",
            **self.kwargs,
        )


class FindCareersPageTask(ActionEvent):
    def __init__(
        self,
        company_name: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_CAREERS_PAGE,
            company_name=company_name.title(),
            **kwargs,
        )
        self.link = None

    def _render_title(self):
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"
        return H3(
            "Searching for the careers page of ",
            CompanyTag(self.company_name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        return (
            Div(
                "Found... ",
                A(
                    self.link,
                    href=self.link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                cls="text-sm",
            )
            if self.link
            else None
        )

    def complete_task(self, link: str):
        super().complete_task()
        self.link = link


class FindOpeningsPageTask(ActionEvent):
    def __init__(
        self,
        careers_link: str,
        company_name: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_OPENINGS_PAGE,
            company_name=company_name.title(),
            **kwargs,
        )
        self.careers_link = careers_link
        self.openings_link: Optional[str] = None

    def _render_title(self):
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"

        return H3(
            "Using",
            OutputInputTag(
                A(
                    self.careers_link,
                    href=self.careers_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                )
            ),
            "to find the page containing the list of openings at",
            CompanyTag(self.company_name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        return (
            Div(
                "Found... ",
                A(
                    self.openings_link,
                    href=self.openings_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                cls="text-sm",
            )
            if self.openings_link
            else None
        )

    def complete_task(self, openings_link: Optional[str]):
        super().complete_task()
        self.openings_link = openings_link


class ParseOpeningsTask(ActionEvent):
    def __init__(
        self,
        company: Company,
        job_type: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.PARSE_OPENINGS,
            company_name=company.name.title(),
            **kwargs,
        )
        self.company = company
        self.job_type = job_type
        self.job_openings = []

    def complete_task(self, openings: List[JobOpening]):
        super().complete_task()
        self.job_openings = openings

    def _render_title(self):
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"

        return H3(
            Span("Parsing "),
            OutputInputTag(
                A(
                    self.company.opening_link,
                    href=str(self.company.opening_link),
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                )
            ),
            Span("for"),
            JobTypeTag(self.job_type),
            "openings at",
            CompanyTag(self.company.name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        sorted_by_location = sorted(
            self.job_openings or [], key=lambda x: x.location or "Unknown", reverse=True
        )
        grouped_by_location = itertools_groupby(
            sorted_by_location,
            lambda x: x.location or "Unknown",
        )

        openings_by_locations = [
            Div(
                H3(location, cls="font-medium text-lg mt-4 mb-2"),
                Ul(*list(openings), cls="list-disc list-inside"),
            )
            for location, openings in grouped_by_location
        ]

        return (
            Div(
                f"Found {self.job_type} jobs in the following locations... ",
                Form(
                    Div(*openings_by_locations),
                    Div(
                        Button(
                            "Find Contacts",
                            svg.Svg(
                                svg.Path(
                                    stroke="currentColor",
                                    stroke_linecap="round",
                                    stroke_linejoin="round",
                                    stroke_width="2",
                                    d="M1 5h12m0 0L9 1m4 4L9 9",
                                ),
                                aria_hidden="true",
                                xmlns="http://www.w3.org/2000/svg",
                                fill="none",
                                viewbox="0 0 14 10",
                                cls="rtl:rotate-180 w-3.5 h-3.5 ms-2",
                            ),
                            type="submit",
                            cls="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
                        ),
                        cls="flex font-medium gap-x-2 mt-8",
                    ),
                    hx_post=f"/contacts_table?company_name={self.company.name}",
                    hx_target="#action_plan_timeline",
                    hx_swap="beforeend",
                    hx_ext="chunked-transfer",
                ),
            )
            if self.job_openings
            else None
        )


class ParseJobDescriptionEvent(ActionEvent):
    def __init__(
        self,
        job: JobOpening,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.PARSE_JOB_DESCRIPTION,
            company_name=job.company.name.title(),
            **kwargs,
        )
        self.job = job
        self.keywords = []
        self.positions = []

    def complete_task(self, keywords: List[str], positions: List[str]):
        super().complete_task()
        self.keywords = keywords
        self.positions = positions

    def _render_title(self):
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"

        return Span(
            H3("Parsing job description for"),
            JobTypeTag(self.job.title),
            H3("at"),
            CompanyTag(self.job.company.name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        return (
            Span(
                H3("Determined keywords ", cls="whitespace-nowrap"),
                *[KeywordTag(keyword) for keyword in self.keywords],
                H3("and roles", cls="whitespace-nowrap"),
                *[PositionTag(position) for position in self.positions],
                H3(
                    " as good indicators for finding contacts.",
                    cls="whitespace-nowrap",
                ),
                cls="text-sm flex gap-x-2 font-medium leading-relaxed max-w-full flex-wrap",
            )
            if self.keywords or self.positions
            else None
        )


class ContactTableEvent:
    def __init__(
        self,
        company: Company,
        job_contacts: List[Tuple[JobOpening, Contact]],
        hidden: bool = False,
        **kwargs,
    ):
        self.company = company
        self.status = TaskStatus.IN_PROGRESS
        self.hidden = hidden
        self.id = "contact-table"
        self.kwargs = kwargs
        self.job_contacts = job_contacts

    def complete_task(self, job_contacts: List[Tuple[JobOpening, Contact]]):
        self.status = TaskStatus.COMPLETED
        self.job_contacts = job_contacts

    def __ft__(self):
        print("RENDERING CONTACT TABLE: ", self.job_contacts)
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
