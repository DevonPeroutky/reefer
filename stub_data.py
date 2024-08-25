from actions.events import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
)
from data_types import Company, JobOpening
from fasthtml.common import Div, Ol, ft

brex = Company(
    name="Brex",
    opening_link="https://www.brex.com/careers#jobsBoard",
    careers_link="https://www.brex.com/careers",
)

test_openings = [
    JobOpening(
        id="0",
        company=brex,
        title="Compliance Manager",
        location="San Francisco, CA",
        link="https://www.brex.com/careers#Compliance-heading",
        related=False,
    ),
    JobOpening(
        id="1",
        company=brex,
        title="Data Scientist",
        location=None,
        link="https://www.brex.com/careers#Data-heading",
        related=True,
    ),
    JobOpening(
        id="17",
        company=brex,
        title="(NEW) Compliance Manager",
        location="New York, NY",
        link="https://www.brex.com/careers#Compliance-heading",
        related=False,
    ),
    JobOpening(
        id="2",
        company=brex,
        title="Designer",
        location=None,
        link="https://www.brex.com/careers#Design-heading",
        related=False,
    ),
    JobOpening(
        id="3",
        company=brex,
        title="Software Engineer",
        location=None,
        link="https://www.brex.com/careers#Engineering-heading",
        related=True,
    ),
    JobOpening(
        id="4",
        company=brex,
        title="Financial Analyst",
        location=None,
        link="https://www.brex.com/careers#Finance-heading",
        related=False,
    ),
    JobOpening(
        id="5",
        company=brex,
        title="Legal Counsel",
        location=None,
        link="https://www.brex.com/careers#Legal-heading",
        related=False,
    ),
    JobOpening(
        id="6",
        company=brex,
        title="Marketing Manager",
        location=None,
        link="https://www.brex.com/careers#Marketing-heading",
        related=False,
    ),
    JobOpening(
        id="7",
        company=brex,
        title="Operations Specialist",
        location=None,
        link="https://www.brex.com/careers#Operations-heading",
        related=False,
    ),
    JobOpening(
        id="8",
        company=brex,
        title="Administrative Assistant",
        location=None,
        link="https://www.brex.com/careers#Other General and Administrative-heading",
        related=False,
    ),
    JobOpening(
        id="9",
        company=brex,
        title="HR Specialist",
        location=None,
        link="https://www.brex.com/careers#People-heading",
        related=False,
    ),
    JobOpening(
        id="10",
        company=brex,
        title="Sales Representative",
        location=None,
        link="https://www.brex.com/careers#Sales-heading",
        related=False,
    ),
]

test_actions = []
spotter_action = FindCareersPageTask(company_name="Spotter")

brex_action = FindCareersPageTask(company_name="Brex")
brex_action.complete_task("https://www.brex.com/careers")

brex_openings_page_action = FindOpeningsPageTask(
    careers_link=str(brex_action.link), company_name=brex_action.company_name
)
brex_openings_page_action.complete_task("https://www.brex.com/careers#jobsBoard")

brex_openings_action = ParseOpeningsTask(
    openings_link=str(brex_openings_page_action.openings_link),
    company=brex,
    job_type="Software Engineer",
)
brex_openings_action.complete_task(test_openings)

# brex_contacts_action = FindContactsTask(
#     company=brex_openings_page_action.company_name,
#     job_id="job-17",
# )

test_actions.append(brex_action)
test_actions.append(brex_openings_page_action)
test_actions.append(brex_openings_action)
# test_actions.append(brex_contacts_action)


TEST_ACTION_PLAN = Div(
    Ol(
        *test_actions,
        id="action_plan_timeline",
        cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
    ),
    cls="container flex flex-col items-start gap-y-4 px-8",
)
