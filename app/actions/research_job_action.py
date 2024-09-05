import asyncio

from typing import Optional, AsyncGenerator, List, Tuple
from fasthtml.common import Safe, to_xml

from app.components.application.contact_table import ContactRow, ContactTable
from app.stub_data import test_openings

from app.actions.events import (
    BaseAction,
    ParseJobDescriptionEvent,
)
from app.services.scraping_service import ScrapingService
from app.services.serp_service import SerpService
from app import Company, Contact, JobOpening


class ResearchJobAction(BaseAction[JobOpening]):
    def __init__(
        self,
        job_opening: JobOpening,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.scraping_service = scraping_service or ScrapingService()
        self.job_opening = job_opening

    async def yield_action_stream(self):

        # TODO: Yield a Job Description loading event
        parse_job_description = ParseJobDescriptionEvent(self.job_opening)
        yield to_xml(parse_job_description)
        await asyncio.sleep(1)

        print(f"Searching for query terms for ", (self.job_opening))
        res = self.scraping_service.find_query_terms_from_job_description(
            self.job_opening
        )
        keywords = res.get("keywords", [])
        positions = res.get("positions", [])

        print("Keywords: ", keywords)
        print("Positions: ", positions)

        parse_job_description.complete_task(keywords=keywords, positions=positions)
        self.job_opening.keywords = keywords
        self.job_opening.positions = positions

        yield to_xml(parse_job_description)
        await asyncio.sleep(0.01)

    def yield_action_result(self) -> JobOpening:
        return self.job_opening
