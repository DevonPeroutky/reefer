import asyncio

from typing import List, Optional, AsyncGenerator, Any
from fasthtml.common import Safe, to_xml

from app.actions import TaskStatus
from app.components.application.timeline_status_indicator import (
    TimelineEventStatusIndicator,
)
from app.components.events.contact_table_event import ContactTableEvent
from app.stub_data import spotter, spotter_openings
from app.actions.find_company_action import FindCompanyAction
from app.actions.parse_openings_action import ParseOpeningsAction
from app.actions.find_contacts_action import FindContactsAction
from app import Company, Contact, JobOpening
from app.actions.research_job_action import ResearchJobAction
from app.services.serp_service import SearchService, SerpService
from app.services.scraping_service import CareersPageScrapingService, ScrapingService
from app.utils.asyncio import combine_generators


"""
Finding contacts for a company is essentially a multi-step process of...

/find_company_information -> /parse_openings -> /research_job_openings -> /find_contacts




1. /find_company_information
    # FindCompanyAction
    a. Finding the company's career page
    b. Finding the page that lists the job openings (which may or may not be the same as the career page)

    # ParseOpeningsAction
    c. Parsing the job openings into a structured list of JobOpening's

2. /parse_openings
    # ResearchJobAction 
    a. Allow user to select which jobs they are interested in
    b. For each job, parse the job description to find relevant keywords and positions that can be used to find contacts

3. /find_contacts
    # FindContactsAction
    a. Use the keywords and positions to find linkedin profiles most relevant to each job opening
    b. Use getprospect API to find emails for each linkedin profile

"""


class Agent:
    def __init__(
        self,
        serp_service: Optional[SearchService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or CareersPageScrapingService()

        self.company: Optional[Company] = None
        self.openings: List[JobOpening] = []
        self.desired_job_openings: List[JobOpening] = []
        self.contacts: List[Contact] = []

    def get_job_opening(self, job_id: str) -> Optional[JobOpening]:
        return next(filter(lambda job: job.id == job_id, self.openings), None)

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

        self.desired_job_openings: List[JobOpening] = list(
            filter(lambda job: job.id in job_ids, openings)
        )
        print("Desired Job Openings: ", self.desired_job_openings)

        research_job_tasks = [
            ResearchJobAction(
                job_opening=job, scraping_service=self.scraping_service
            ).yield_action_stream()
            for job in self.desired_job_openings
        ]

        async for res in combine_generators(*research_job_tasks):
            yield res
            await asyncio.sleep(0.1)

        contact_table = ContactTableEvent(
            id="contact-table", company=self.company or spotter, job_contacts=[]
        )
        yield to_xml(contact_table)
        # await asyncio.sleep(0.1)

    async def find_contacts(self, job_openings: List[JobOpening]):

        find_contacts_tasks = [
            FindContactsAction(
                serp_service=self.serp_service,
                scraping_service=self.scraping_service,
            ).yield_action_stream(job)
            for job in job_openings
        ]

        async for res in combine_generators(*find_contacts_tasks):
            yield res
            await asyncio.sleep(0.1)
