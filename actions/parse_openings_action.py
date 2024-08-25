import asyncio

from typing import Optional, AsyncGenerator, List
from fasthtml.common import Safe, to_xml
from stub_data import test_openings

from actions.events import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    BaseAction,
    ParseOpeningsTask,
)
from services.serp_service import SerpService
from services.scraping_service import ScrapingService
from data_types import Company, Contact, JobOpening
from enums import TaskStatus, TaskType


class ParseOpeningsAction(BaseAction[List[JobOpening]]):
    def __init__(
        self,
        company: Company,
        job_type: str,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.company = company
        self.job_type = job_type
        self.scraping_service = scraping_service or ScrapingService()
        self.openings = []

    async def yield_action_stream(
        self, company_name: str
    ) -> AsyncGenerator[Safe, None]:
        self.company_name = company_name

        event = ParseOpeningsTask(company=self.company, job_type=self.job_type)
        yield to_xml(event)
        await asyncio.sleep(1)

        # job_openings = self.scraping_service.parse_openings_from_link(
        #     company=self.company,
        #     job_type=self.job_type,
        # )
        job_openings = test_openings
        self.openings = job_openings

        event.complete_task(openings=job_openings)

        yield to_xml(event)
        await asyncio.sleep(1)

    def yield_action_result(self):
        return self.openings
