import asyncio

from typing import Optional, AsyncGenerator, List
from fasthtml.common import Safe, to_xml
from app.actions import BaseAction
from app.stub_data import test_openings

from app.components.events import (
    ContactTableEvent,
    ParseOpeningsTask,
)
from app.services.scraping_service import CareersPageScrapingService, ScrapingService
from app import Company, Contact, JobOpening


class ParseOpeningsAction(BaseAction[List[JobOpening]]):
    def __init__(
        self,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.scraping_service = scraping_service or CareersPageScrapingService()
        self.openings = []

    async def yield_action_stream(
        self, company: Company, job_type: str
    ) -> AsyncGenerator[Safe, None]:

        event = ParseOpeningsTask(company=company, job_type=job_type)
        yield to_xml(event)
        await asyncio.sleep(1)

        job_openings = self.scraping_service.parse_openings_from_link(
            company=company,
            job_type=job_type,
        )
        # job_openings = test_openings
        self.openings = job_openings

        event.complete_task(openings=job_openings)

        yield to_xml(event)
        await asyncio.sleep(0.1)

    def yield_action_result(self):
        return self.openings
