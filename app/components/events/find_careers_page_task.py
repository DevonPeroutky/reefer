from app import Company
from app.agent import AgentState
from app.agent.knowledge_service import KnowledgeService
from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag
from app.actions import TaskStatus, TaskType
from fasthtml.common import *

from app.services.serp_service import SearchService, SerpService


class FindCareersPageTask(ActionEvent[str]):
    def __init__(
        self,
        knowledge_service: Optional[KnowledgeService] = None,
        serp_service: Optional[SearchService] = None,
        **kwargs,
    ):
        super().__init__(
            knowledge_service=knowledge_service,
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_CAREERS_PAGE,
            **kwargs,
        )
        self.serp_service: SearchService = serp_service or SerpService()

    def execute_task(self, state: AgentState):
        assert (
            state.company
        ), "Company must be set in the state before executing this task"
        careers_page_url = self.serp_service.find_careers_url(state.company.name)

        # Update the company state with the careers page link
        state.company.careers_link = careers_page_url
        super().complete_task()

    def _render_title(self):
        agent_state = self.get_current_state()
        assert agent_state.company, "Company must be set before rendering the title"
        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"
        return H3(
            "Searching for the careers page of ",
            CompanyTag(agent_state.company.name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        agent_state = self.get_current_state()
        return (
            Div(
                "Found... ",
                A(
                    agent_state.company.careers_link,
                    href=agent_state.company.careers_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                cls="text-sm",
            )
            if agent_state.company and agent_state.company.careers_link
            else None
        )
