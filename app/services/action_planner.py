from typing import List, Optional

from app.actions.find_company_action import FindCompanyAction
from app.actions.parse_openings_action import ParseOpeningsAction
from app.actions.find_contacts_action import FindContactsAction
from app import Company, Contact, JobOpening
from app.services.serp_service import SerpService
from app.services.scraping_service import ScrapingService


class Agent:
    def __init__(
        self,
        serp_service: Optional[SerpService] = None,
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
            yield event

        self.company = find_company_action.yield_action_result()
        print(f"TODO: Asynchronously write ({self.company} to DB")

        # 2. Parse openings
        parse_openings_action = ParseOpeningsAction()
        async for event in parse_openings_action.yield_action_stream(
            company=self.company, job_type="Software Engineer"
        ):
            yield event

        self.openings = parse_openings_action.yield_action_result()
        print(self.openings)
        print(f"TODO: Asynchronously write {self.openings} to DB")

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
