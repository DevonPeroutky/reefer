from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag, OutputInputTag
from app.actions import TaskStatus, TaskType
from fasthtml.common import *
from typing import Optional


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
