from abc import abstractmethod
from uuid import uuid4
from typing import Optional
from fasthtml.common import *

from app.components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from app.actions import TaskStatus, TaskType


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
            **self.kwargs,
        )
