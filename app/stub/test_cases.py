from app.components.events import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
)
from app import Company, Contact, JobOpening
from fasthtml.common import Div, Ol, ft
from app.stub.services import DummySearchService, DummyScrapingService
from app.stub.data import brex, test_contacts, test_openings


test_actions = []
spotter_action = FindCareersPageTask(serp_service=DummySearchService())

brex_action = FindCareersPageTask(serp_service=DummySearchService())
brex_action.complete_task("https://www.brex.com/careers")

brex_openings_page_action = FindOpeningsPageTask(
    scraping_service=DummyScrapingService()
)
brex_openings_page_action.complete_task("https://www.brex.com/careers#jobsBoard")

brex_openings_action = ParseOpeningsTask(
    openings_link=str(brex_openings_page_action.openings_link),
    company=brex,
    job_type="Software Engineer",
)
brex_openings_action.complete_task(test_openings)

test_actions.append(brex_action)
test_actions.append(brex_openings_page_action)
test_actions.append(brex_openings_action)


TEST_ACTION_PLAN = Div(
    Ol(
        *test_actions,
        id="action_plan_timeline",
        cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
    ),
    cls="container flex flex-col items-start gap-y-4 px-8",
)
