import time
import random
import asyncio

from typing import Optional, AsyncGenerator
from fasthtml.common import Safe, to_xml

from app.actions import BaseAction
from app.components.events.parse_job_description_event import ParseJobDescriptionEvent

from app.services.scraping_service import ScrapingService
from app import JobOpening


class ResearchJobAction(BaseAction[JobOpening]):
    def __init__(
        self,
        job_opening: JobOpening,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.scraping_service = scraping_service or ScrapingService()
        self.job_opening = job_opening

    async def yield_action_stream(self) -> AsyncGenerator[Safe, None]:

        # TODO: Yield a Job Description loading event
        parse_job_description = ParseJobDescriptionEvent(self.job_opening)
        yield to_xml(parse_job_description)
        await asyncio.sleep(0.1)

        print(
            f"Searching for query terms for ",
            (self.job_opening),
            "in a seperate thread...",
        )
        res = await asyncio.to_thread(
            self.scraping_service.find_query_terms_from_job_description,
            self.job_opening,
        )
        keywords = res.get("keywords", [])
        positions = res.get("positions", [])

        parse_job_description.complete_task(keywords=keywords, positions=positions)
        self.job_opening.keywords = keywords
        self.job_opening.positions = positions

        yield to_xml(parse_job_description)
        await asyncio.sleep(0.01)

    def yield_action_result(self) -> JobOpening:
        return self.job_opening
