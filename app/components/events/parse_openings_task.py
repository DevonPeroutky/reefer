from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag, JobTypeTag, OutputInputTag
from app.actions import TaskStatus, TaskType
from fasthtml.common import *
from app import Company, JobOpening
from typing import List
from itertools import groupby as itertools_groupby


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
