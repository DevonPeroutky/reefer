import asyncio
from asyncio import create_task
from actions.events import (
    ActionEvent,
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
    TaskType,
)
from actions.find_company_action import FindCompanyAction
from actions.parse_openings_action import ParseOpeningsAction
from typing import List, Optional, cast

from services.serp_service import SerpService
from services.scraping_service import ScrapingService
from data_types import Company, JobOpening


class Agent:
    def __init__(
        self,
        serp_service: Optional[SerpService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or ScrapingService()

    async def test_timeline_event_generator(self, company_name: str):

        # 1. Find company
        find_company_action = FindCompanyAction(
            serp_service=self.serp_service,
            scraping_service=self.scraping_service,
        )

        async for event in find_company_action.yield_action_stream(company_name):
            yield event

        company = find_company_action.yield_action_result()
        print(f"TODO: Asynchronously write ({company} to DB")

        # 2. Parse openings
        parse_openings_action = ParseOpeningsAction(
            company=company, job_type="Software Engineer"
        )
        async for event in parse_openings_action.yield_action_stream(company_name):
            yield event
        openings = parse_openings_action.yield_action_result()
        print(f"TODO: Asynchronously write {openings} to DB")

    def perform_action(self, task: ActionEvent):
        match (task.task_type):
            case TaskType.FIND_CAREERS_PAGE:
                task = cast(FindCareersPageTask, task)
                careers_link = self.serp_service.find_careers_url(task.company)
                task.complete_task(link=careers_link)
                return careers_link
            case TaskType.FIND_OPENINGS_PAGE:
                task = cast(FindOpeningsPageTask, task)
                openings_link = (
                    self.scraping_service.find_openings_page_link(
                        link=task.careers_link, company=task.company
                    )
                    or task.careers_link
                )
                task.complete_task(openings_link=openings_link)
                return openings_link
            case TaskType.PARSE_OPENINGS:
                task = cast(ParseOpeningsTask, task)
                assert task and task.company.opening_link, "Openings link not found"
                openings = self.scraping_service.parse_openings_from_link(
                    openings_link=task.company.opening_link,
                    company=task.company,
                    job_type=task.job_type,
                )
                task.complete_task(openings=openings)
                return openings
            case TaskType.FIND_CONTACTS:
                task = cast(ParseOpeningsTask, task)
                assert task and task.job_openings, "Openings link not found"

                return None

            case TaskType.PARSE_JOB_DESCRIPTION:
                return None

    async def yield_company_information(self, company_name: str):
        find_careers_page_task = FindCareersPageTask(company=company_name)
        yield to_xml(find_careers_page_task)
        await asyncio.sleep(1)

        # careers_page_url: str = self.perform_action(find_careers_page_task)
        # print("Careers page URL: ", careers_page_url)
        # assert careers_page_url is not None, "Careers page URL not found"
        # yield to_xml(find_careers_page_task)
        careers_page_url = "https://www.brex.com/careers"
        find_careers_page_task.complete_task("https://www.brex.com/careers")
        yield to_xml(find_careers_page_task)
        await asyncio.sleep(1)

        # -----------------------
        # TASK: FIND OPENINGS PAGE
        # -----------------------
        find_openings_page_task = FindOpeningsPageTask(
            careers_link=str(careers_page_url), company_name=company_name
        )
        yield to_xml(find_openings_page_task)
        await asyncio.sleep(1)

        # openings_page_url: str = self.perform_action(find_openings_page_task)
        openings_page_url = "https://www.brex.com/careers#jobsBoard"
        find_openings_page_task.complete_task(openings_page_url)
        print("Openings page URL: ", openings_page_url)
        yield to_xml(find_openings_page_task)
        await asyncio.sleep(0.01)

        yield Company(
            name=company_name,
            careers_link=careers_page_url,
            opening_link=openings_page_url,
        )

    async def yield_openings(self, company: Company, job_type: str):
        parse_openings_task = ParseOpeningsTask(
            company=company,
            job_type=job_type,
        )
        yield to_xml(parse_openings_task)
        await asyncio.sleep(1)

        # openings = self.perform_action(parse_openings_task)
        openings = test_openings
        parse_openings_task.complete_task(openings)
        yield to_xml(parse_openings_task)

        yield openings

    async def yield_contacts(self, company: Company, jobs: List[JobOpening]):
        for job in jobs:
            find_contacts_task = FindContactsTask(company=company, job_id=job.id)
            yield to_xml(find_contacts_task)
            await asyncio.sleep(1)

            contacts = self.perform_action(find_contacts_task)
            find_contacts_task.complete_task(contacts)
            yield to_xml(find_contacts_task)

            yield contacts
