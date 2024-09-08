from app.components.events import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
)
from app import Company, Contact, JobOpening
from fasthtml.common import Div, Ol, ft

brex = Company(
    name="Brex",
    opening_link="https://www.brex.com/careers#jobsBoard",
    careers_link="https://www.brex.com/careers",
)

spotter = Company(
    name="Spotter",
    opening_link="https://job-boards.greenhouse.io/spotter",
    careers_link="https://job-boards.greenhouse.io/spotter",
)


spotter_openings = [
    JobOpening(
        id="0",
        company=spotter,
        title="AI Engineer",
        location="Los Angeles, CA",
        link="https://job-boards.greenhouse.io/spotter/jobs/4413256005",
        related=True,
        keywords=["AI", "Machine Learning", "Python"],
        positions=["Engineering Manager", "Product Manager"],
    ),
    JobOpening(
        id="1",
        company=spotter,
        title="Senior AI Prompt Engineer",
        location="Los Angeles, CA",
        link="https://job-boards.greenhouse.io/spotter/jobs/4417247005",
        related=True,
        keywords=["AI", "Machine Learning", "Python"],
        positions=["Engineering Manager", "Senior Engineer"],
    ),
]

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


test_contacts = [
    Contact(
        name="Pedro Franceschi",
        job_title="Software Engineer",
        location="San Francisco",
        email="pedro@brex.com",
        company=brex,
    ),
    # Contact(
    #     name="Jane Smith",
    #     job_title="Engineering Manager",
    #     location="San Francisco",
    #     email="",
    #     company=brex,
    # ),
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
