import asyncio

from typing import Optional, AsyncGenerator, List, Tuple
from fasthtml.common import Safe, Search, to_xml

from app.actions import BaseAction
from app.components.application.contact_table import ContactRow, ContactTable
from app.stub_data import test_openings

from app.components.events import (
    ContactTableEvent,
    ParseJobDescriptionEvent,
)
from app.services.scraping_service import CareersPageScrapingService, ScrapingService
from app.services.serp_service import SearchService, SerpService
from app import Company, Contact, JobOpening


class FindContactsAction(BaseAction[List[Contact]]):
    def __init__(
        self,
        company: Company,
        job_type: str,
        serp_service: Optional[SearchService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.company = company
        self.job_type = job_type
        self.scraping_service = scraping_service or CareersPageScrapingService()
        self.serp_service = serp_service or SerpService()
        self.contacts = []

    async def yield_action_stream(
        self, jobs: List[JobOpening]
    ) -> AsyncGenerator[Safe, None]:

        job_search_payload = []
        for job in jobs:
            # TODO: Yield a Job Description loading event
            parse_job_description = ParseJobDescriptionEvent(job)
            yield to_xml(parse_job_description)
            await asyncio.sleep(1)

            print(f"Searching for query terms for ", (job))
            res = self.scraping_service.find_query_terms_from_job_description(job)
            keywords = res.get("keywords", [])
            positions = res.get("positions", [])

            print("Keywords: ", keywords)
            print("Positions: ", positions)

            parse_job_description.complete_task(keywords=keywords, positions=positions)
            job_search_payload.append((job, keywords, positions))

            yield to_xml(parse_job_description)
            await asyncio.sleep(0.01)

        contact_table = ContactTableEvent(company=self.company, job_contacts=[])
        yield to_xml(contact_table)
        await asyncio.sleep(0.1)

        job_contacts: List[Tuple[JobOpening, Contact]] = []
        for job, keywords, positions in job_search_payload:
            print(
                f"Searching for contacts for {job.title} using {keywords} and {positions}"
            )

            contacts = self.serp_service.find_list_of_contacts(
                company=job.company,
                keywords=keywords,
                targetted_roles=positions,
            )
            for contact in contacts:
                job_contacts.append((job, contact))

        contact_table.complete_task(job_contacts=job_contacts)
        yield to_xml(contact_table)
        await asyncio.sleep(1)

    def yield_action_result(self) -> List[Contact]:
        return self.contacts
