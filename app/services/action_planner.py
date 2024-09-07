import asyncio

from typing import List, Optional, AsyncGenerator, Any
from fasthtml.common import Safe, to_xml

from app.components.events.contact_table_event import ContactTableEvent
from app.components.events.parse_job_description_event import ParseJobDescriptionEvent
from app.stub_data import spotter, spotter_openings
from app.actions.find_company_action import FindCompanyAction
from app.actions.parse_openings_action import ParseOpeningsAction
from app.actions.find_contacts_action import FindContactsAction
from app import Company, Contact, JobOpening
from app.actions.research_job_action import ResearchJobAction
from app.services.serp_service import SearchService, SerpService
from app.services.scraping_service import ScrapingService
from app.utils.asyncio import combine_generators


class Agent:
    def __init__(
        self,
        serp_service: Optional[SearchService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or ScrapingService()

        self.company: Optional[Company] = None
        self.openings: List[JobOpening] = []
        self.contacts: List[Contact] = []

    async def find_company_information(self, company_name: str):

        # 1. Find company
        find_company_action = FindCompanyAction(
            serp_service=self.serp_service,
            scraping_service=self.scraping_service,
        )

        async for event in find_company_action.yield_action_stream(company_name):
            print("Yielding event: ", event)
            yield event

        self.company = find_company_action.yield_action_result()
        print(f"TODO: Asynchronously write ({self.company} to DB")

        # 2. Parse openings
        parse_openings_action = ParseOpeningsAction(
            scraping_service=self.scraping_service
        )
        async for event in parse_openings_action.yield_action_stream(
            company=self.company, job_type="Software Engineer"
        ):
            print("Yielding parse openings: ", event)
            yield event

        self.openings = parse_openings_action.yield_action_result()
        print(self.openings)
        print(f"TODO: Asynchronously write {self.openings} to DB")

    async def research_job_openings(self, job_ids: List[str]):
        openings = self.openings or spotter_openings
        # assert self.company, "Company is not determined?"

        # TODO: REMOVE THIS OR
        desired_job_openings = (
            list(filter(lambda job: job.id in job_ids, openings)) or spotter_openings
        )
        print("Desired Job Openings: ", desired_job_openings)

        generators = [
            ResearchJobAction(
                job_opening=job, scraping_service=self.scraping_service
            ).yield_action_stream()
            for job in desired_job_openings
        ]

        # WHY ARE "CONNECTIONS" STILL OPEN?
        async for res in combine_generators(*generators):
            yield res

        print("YIELDing the TABLE")
        # Yield the (empty) contact_table
        contact_table = ContactTableEvent(
            company=self.company or spotter, job_contacts=[]
        )
        yield to_xml(contact_table)
        # await asyncio.sleep(0.1)

    async def find_contacts(self, job_ids: List[str]):
        assert self.company, "Company is not determined?"

        desired_job_openings = list(
            filter(lambda job: job.id in job_ids, self.openings)
        )
        print("Desired Job Openings: ", desired_job_openings)

        find_contacts_action = FindContactsAction(
            company=self.company,
            job_type="Software Engineer",
            serp_service=self.serp_service,
            scraping_service=self.scraping_service,
        )

        async for event in find_contacts_action.yield_action_stream(
            desired_job_openings
        ):
            yield event
