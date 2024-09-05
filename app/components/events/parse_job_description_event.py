from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag, JobTypeTag, KeywordTag, PositionTag
from app.actions import TaskStatus, TaskType
from fasthtml.common import *
from app import JobOpening
from typing import List


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
