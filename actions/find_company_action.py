import asyncio

from typing import List, Optional, TypeVar, Generic, AsyncGenerator
from fasthtml.common import Safe, to_xml

from actions.events import (
    ContactTableEvent,
    FindCareersPageTask,
    FindOpeningsPageTask,
    BaseAction,
)
from components.application.contact_table import ContactTable
from services.serp_service import SerpService
from services.scraping_service import ScrapingService
from data_types import Company, Contact, JobOpening
from enums import TaskStatus, TaskType


class FindCompanyAction(BaseAction[Company]):
    def __init__(
        self,
        serp_service: Optional[SerpService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or ScrapingService()
        self.status = TaskStatus.IN_PROGRESS
        self.openings_link = None
        self.careers_link = None
        self.company: Optional[Company] = None

    async def yield_action_stream(
        self, company_name: str
    ) -> AsyncGenerator[Safe, None]:
        self.company_name = company_name

        event = FindCareersPageTask(company_name=company_name)
        yield to_xml(event)
        await asyncio.sleep(0.1)

        # careers_page_url = self.serp_service.find_careers_url(event.company_name)
        careers_page_url = "https://www.brex.com/careers"

        event.complete_task(link=careers_page_url)

        yield to_xml(event)
        await asyncio.sleep(0.1)

        # -----------------------
        # TASK: FIND OPENINGS PAGE
        # -----------------------
        find_openings_page_event = FindOpeningsPageTask(
            careers_link=str(careers_page_url), company_name=company_name
        )
        yield to_xml(find_openings_page_event)
        await asyncio.sleep(0.1)

        # openings_page_url = (
        #     self.scraping_service.find_openings_page_link(
        #         link=careers_page_url, company=event.company_name
        #     )
        #     or careers_page_url
        # )
        openings_page_url = "https://www.brex.com/careers#jobsBoard"

        # Store the found information
        self.careers_link = careers_page_url
        self.openings_link = openings_page_url

        find_openings_page_event.complete_task(openings_link=openings_page_url)

        yield to_xml(find_openings_page_event)

    def yield_action_result(self) -> Company:
        return Company(
            name=self.company_name,
            careers_link=self.careers_link,
            opening_link=self.openings_link,
        )
