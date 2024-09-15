from abc import abstractmethod
from uuid import uuid4
from typing import AsyncGenerator, Optional, Generic, TypeVar
from fasthtml.common import *
from app.agent import AgentState

from app.agent.knowledge_service import KnowledgeService
from app.components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from app.actions import TaskStatus, TaskType

T = TypeVar("T")


class ActionEvent(Generic[T]):
    def __init__(
        self,
        status: TaskStatus,
        task_type: TaskType,
        knowledge_service: Optional[KnowledgeService] = None,
        id: Optional[str] = None,
        **kwargs,
    ):
        self.id = str(id) if id is not None else str(uuid4())
        self.knowledge_service = knowledge_service or KnowledgeService()
        self.status = status
        self.task_type = task_type
        self.kwargs = kwargs

    def get_current_state(self) -> AgentState:
        print("Current State: ", self.knowledge_service.get_current_state())
        return self.knowledge_service.get_current_state()

    @abstractmethod
    async def execute_task(self, state: AgentState):
        pass

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


class StreamingActionEvent(ActionEvent):
    @abstractmethod
    def execute_streaming_task(self, *args, **kwargs) -> AsyncGenerator[str, None]:
        pass
