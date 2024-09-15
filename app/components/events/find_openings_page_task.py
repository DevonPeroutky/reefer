from app import Company
from app.agent import AgentState
from app.agent.knowledge_service import KnowledgeService
from app.components.events import ActionEvent
from app.components.primitives.tag import CompanyTag, OutputInputTag
from app.actions import TaskStatus, TaskType
from app.services.scraping_service import ScrapingService, CareersPageScrapingService
from fasthtml.common import *
from typing import Optional


class FindOpeningsPageTask(ActionEvent[Company]):
    def __init__(
        self,
        knowledge_service: Optional[KnowledgeService] = None,
        scraping_service: Optional[ScrapingService] = None,
        **kwargs,
    ):
        super().__init__(
            knowledge_service=knowledge_service,
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_OPENINGS_PAGE,
            **kwargs,
        )
        self.scraping_service: ScrapingService = (
            scraping_service or CareersPageScrapingService()
        )

    def execute_task(self, state: AgentState):
        assert (
            state and state.company and state.company.careers_link
        ), "Company must be set in the state before executing this task"

        openings_page_url = (
            self.scraping_service.find_openings_page_link(
                link=state.company.careers_link, company=state.company.name
            )
            or state.company.careers_link
        )
        state.company.opening_link = openings_page_url

        super().complete_task()

    def _render_title(self):
        company = self.get_current_state().company
        assert (
            company and company.careers_link
        ), "Company must be set before rendering the title"

        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"

        return H3(
            "Using",
            OutputInputTag(
                A(
                    company.careers_link,
                    href=company.careers_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                )
            ),
            "to find the page containing the list of openings at",
            CompanyTag(company.name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        company = self.get_current_state().company
        return (
            Div(
                "Found... ",
                A(
                    company.opening_link,
                    href=company.opening_link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                cls="text-sm",
            )
            if company and company.opening_link
            else None
        )
