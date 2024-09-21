import time
from app.agent import AgentState
from app.agent.knowledge_service import KnowledgeService
from app.components.events import ActionEvent
from app.components.events.action_event import TimelineActionEvent
from app.components.events.action_event import TimelineActionEvent
from app.components.primitives.tag import (
    CompanyTag,
    JobTypeTag,
    KeywordTag,
    PositionTag,
)
from app import TaskStatus, TaskType
from fasthtml.common import *
from app import JobOpening
from typing import List

from app.services.scraping_service import CareersPageScrapingService, ScrapingService


class ParseJobDescriptionTask(TimelineActionEvent):
    def __init__(
        self,
        job: JobOpening,
        scraping_service: Optional[ScrapingService] = None,
        knowledge_service: Optional[KnowledgeService] = None,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            knowledge_service=knowledge_service,
            task_type=TaskType.PARSE_JOB_DESCRIPTION,
            **kwargs,
        )
        self.scraping_service: ScrapingService = (
            scraping_service or CareersPageScrapingService()
        )
        self.job = job

    async def execute_timeline_task(self, state: AgentState):
        print(
            f"Searching for query terms for ",
            (self.job),
            "in a seperate thread...",
        )
        res = await self.scraping_service.find_query_terms_from_job_description(
            self.job
        )
        keywords = res.get("keywords", [])
        positions = res.get("positions", [])
        self.job.keywords = keywords
        self.job.positions = positions

        self.knowledge_service.upsert_job_opening(job_opening=self.job)
        super().complete_task()

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
                *[KeywordTag(keyword) for keyword in self.job.keywords],
                H3("and roles", cls="whitespace-nowrap"),
                *[PositionTag(position) for position in self.job.positions],
                H3(
                    " as good indicators for finding contacts.",
                    cls="whitespace-nowrap",
                ),
                cls="text-sm flex gap-x-2 font-medium leading-relaxed max-w-full flex-wrap",
            )
            if self.job.keywords or self.job.positions
            else None
        )
