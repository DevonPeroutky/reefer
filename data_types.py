import fasthtml.svg as svg
from itertools import groupby as itertools_groupby
from uuid import uuid3

from uuid import uuid4
from typing import List, Optional
from fasthtml.common import *
from dataclasses import dataclass
from fasthtml.common import Div, Span, Li, H3, P, to_xml

from components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from components.primitives.tag import (
    CompanyTag,
    JobTypeTag,
    OutputInputTag,
)
from enums import TaskStatus, TaskType


@dataclass
class JobOpening:
    id: str
    title: str
    location: Optional[str]
    link: str
    related: bool

    def __ft__(self):
        location = P(
            " (" + self.location + ")" if self.location else "",
        )
        return Div(
            Input(
                id="default-checkbox",
                type="checkbox",
                name="jobs",
                value=f"item-{self.id}",
                cls="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            ),
            Label(
                A(
                    self.title,
                    href=self.link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                fr="default-checkbox",
                cls="ms-2 font-medium text-gray-900 dark:text-gray-300",
            ),
            cls="flex items-center mb-2",
            id=f"item-{self.id}",
        )


class ActionEvent:
    def __init__(
        self,
        company: str,
        status: TaskStatus,
        task_type: TaskType,
        id: Optional[str] = None,
        **kwargs,
    ):
        self.id = str(id) if id is not None else str(uuid4())
        self.status = status
        self.task_type = task_type
        self.kwargs = kwargs
        self.company = company

    def _prepare_for_dom_update(self):
        self.kwargs["hx_swap_oob"] = "true"

    def complete_task(self):
        self.status = TaskStatus.COMPLETED
        self._prepare_for_dom_update()

    def _render_title(self):
        pass

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
        company: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_CAREERS_PAGE,
            company=company.title(),
            **kwargs,
        )
        self.link = None

    def _render_title(self):
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"
        return H3(
            "Searching for the careers page of ",
            CompanyTag(self.company.title()),
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
        company: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_OPENINGS_PAGE,
            company=company.title(),
            **kwargs,
        )
        self.careers_link = careers_link

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
            CompanyTag(self.company),
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
        openings_link: str,
        company: str,
        job_type: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.PARSE_OPENINGS,
            company=company.title(),
            **kwargs,
        )
        self.openings_link = openings_link
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
                    self.openings_link,
                    href=self.openings_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                )
            ),
            Span("for"),
            JobTypeTag(self.job_type),
            "openings at",
            CompanyTag(self.company),
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
                    hx_post="/find_contacts",
                    hx_swap="afterend",
                ),
            )
            if self.job_openings
            else None
        )


class FindContactsTask(ActionEvent):
    def __init__(
        self,
        company: str,
        job_ids: str,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.PARSE_OPENINGS,
            company=company,
            **kwargs,
        )
        self.job_ids = job_ids
