import asyncio

from typing import Optional, AsyncGenerator, List, Tuple
from fasthtml.common import Safe, Search, to_xml

from app.actions import BaseAction
from app.components.application.contact_table import ContactRow

from app.services.scraping_service import CareersPageScrapingService, ScrapingService
from app.services.serp_service import SearchService, SerpService
from app import Contact, JobOpening


class FindContactsAction(BaseAction[List[Contact]]):
    def __init__(
        self,
        serp_service: Optional[SearchService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.scraping_service = scraping_service or CareersPageScrapingService()
        self.serp_service = serp_service or SerpService()
        self.contacts = []

    async def yield_action_stream(self, job: JobOpening) -> AsyncGenerator[Safe, None]:

        print(
            f"Searching for contacts for {job.title} using {job.keywords} and {job.positions}"
        )

        contacts = await asyncio.to_thread(
            self.serp_service.find_list_of_contacts,
            job.company,
            job.keywords,
            job.positions,
        )

        print("Found contacts: ", contacts)

        self.contacts = contacts

        for contact_row in list(map(lambda c: ContactRow(job, c), contacts)):
            yield to_xml(contact_row)
            await asyncio.sleep(1)

    def yield_action_result(self) -> List[Contact]:
        return self.contacts
