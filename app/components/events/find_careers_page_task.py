from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag
from app.actions import TaskStatus, TaskType
from fasthtml.common import *


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
