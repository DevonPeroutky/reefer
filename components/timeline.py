import fasthtml.svg as svg
from fasthtml.common import Div, Span, Li, H3, P, Ol
from fasthtml.common import ft_html, to_xml

from components.primitives.spinner import Spinner
from components.primitives.success_icon import SearchIcon, SuccessIcon
from data_types import TaskStatus


class TimelineEventStatusIndidcator:
    def __init__(self, status: TaskStatus, id: str):
        self.status = status
        self.id = id

    def __ft__(self):
        if self.status == TaskStatus.PENDING:
            return to_xml(
                SearchIcon(
                    id=f"{self.id}-loader",
                    cls="absolute flex items-center justify-center w-8 h-8 bg-gray-200 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900",
                )
            )
        elif self.status == TaskStatus.IN_PROGRESS:
            return to_xml(
                Spinner(
                    id=f"{self.id}-loader",
                    cls="absolute flex items-center justify-center w-8 h-8 bg-white rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900",
                )
            )
        elif self.status == TaskStatus.COMPLETED:
            return to_xml(SuccessIcon(id=f"{self.id}-loader"))
        else:
            return to_xml(SearchIcon(id=f"{self.id}-loader"))


class TimelineEvent:
    def __init__(
        self,
        id,
        title: str,
        status: TaskStatus,
        task_type: str,
        **kwargs,
    ):
        self.id = id
        self.title = title
        self.status = status
        self.task_type = task_type
        self.kwargs = kwargs

    def __ft__(self):
        return Li(
            TimelineEventStatusIndidcator(self.status, self.id),
            H3(self.title, cls="font-medium leading-tight"),
            P("Step details here", cls="text-sm"),
            cls="ms-6",
            id=f"item-{self.id}",
            # sse_swap=f"sse-item-{self.id}",
            **self.kwargs,
        )


class Timeline:
    def __init__(self, id: str, events):
        self.id = id
        self.events = events

    def __ft__(self):
        return Ol(
            *self.events,
            id=self.id,
            hx_post="/stream_action_plan",
            hx_trigger="load",
            # hx_target=f"#{self.id}",
            hx_swap="beforeend",
            # hx_swap="innerHTML",
            hx_ext="chunked-transfer",
            cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
        )
