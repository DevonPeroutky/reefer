import asyncio

from fasthtml.common import *

from starlette.responses import StreamingResponse
from components.primitives.search_input import SearchInput
from data_types import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    JobOpening,
    ParseOpeningsTask,
)
from components.timeline import Timeline
from enums import TaskType
from services.action_planner import Agent

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"

custom_script = Script(
    """
    document.body.addEventListener('htmx:configRequest', function(evt) {
        evt.detail.headers['HX-Debug'] = '1';
    });
    """
)
custom_styles = Style(
    """
    ol:empty {
        display: none;
    }

    .htmx-indicator {
        display: None;
    }

    .htmx-request .htmx-indicator {
        opacity: 1;
    }

    /* To ensure the htmx-request itself is affected */
    .htmx-request.htmx-indicator {
        opacity: 1;
        display: block;
    }

    """
)
hdrs = (
    # Flowbite CSS
    Link(href=f"{flowurl}/flowbite.min.css", rel="stylesheet"),
    Meta(name="theme-color", content="#ffffff"),
    # Tailwind CSS
    Script(src="https://cdn.tailwindcss.com"),
    # HTMX
    # Script(src="https://unpkg.com/htmx.org@1.9.12"),
    # Ext
    # Script(src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js"),
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js"
    ),
    custom_styles,
    custom_script,
)

test_openings = [
    JobOpening(
        id="0",
        title="Compliance Manager",
        location="San Francisco, CA",
        link="https://www.brex.com/careers#Compliance-heading",
        related=False,
    ),
    JobOpening(
        id="1",
        title="Data Scientist",
        location=None,
        link="https://www.brex.com/careers#Data-heading",
        related=True,
    ),
    JobOpening(
        id="0",
        title="(NEW) Compliance Manager",
        location="New York, NY",
        link="https://www.brex.com/careers#Compliance-heading",
        related=False,
    ),
    JobOpening(
        id="2",
        title="Designer",
        location=None,
        link="https://www.brex.com/careers#Design-heading",
        related=False,
    ),
    JobOpening(
        id="3",
        title="Software Engineer",
        location=None,
        link="https://www.brex.com/careers#Engineering-heading",
        related=True,
    ),
    JobOpening(
        id="4",
        title="Financial Analyst",
        location=None,
        link="https://www.brex.com/careers#Finance-heading",
        related=False,
    ),
    JobOpening(
        id="5",
        title="Legal Counsel",
        location=None,
        link="https://www.brex.com/careers#Legal-heading",
        related=False,
    ),
    JobOpening(
        id="6",
        title="Marketing Manager",
        location=None,
        link="https://www.brex.com/careers#Marketing-heading",
        related=False,
    ),
    JobOpening(
        id="7",
        title="Operations Specialist",
        location=None,
        link="https://www.brex.com/careers#Operations-heading",
        related=False,
    ),
    JobOpening(
        id="8",
        title="Administrative Assistant",
        location=None,
        link="https://www.brex.com/careers#Other General and Administrative-heading",
        related=False,
    ),
    JobOpening(
        id="9",
        title="HR Specialist",
        location=None,
        link="https://www.brex.com/careers#People-heading",
        related=False,
    ),
    JobOpening(
        id="10",
        title="Sales Representative",
        location=None,
        link="https://www.brex.com/careers#Sales-heading",
        related=False,
    ),
]


app = FastHTML(hdrs=hdrs, live=True)

test_actions = []
spotter_action = FindCareersPageTask(company="Spotter")

brex_action = FindCareersPageTask(company="Brex")
brex_action.complete_task("https://www.brex.com/careers")

brex_openings_page_action = FindOpeningsPageTask(
    careers_link=str(brex_action.link), company=brex_action.company
)
brex_openings_page_action.complete_task("https://www.brex.com/careers#jobsBoard")

brex_openings_action = ParseOpeningsTask(
    openings_link=str(brex_openings_page_action.openings_link),
    company=brex_openings_page_action.company,
    job_type="Software Engineer",
)
brex_openings_action.complete_task(test_openings)

test_actions.append(brex_action)
test_actions.append(brex_openings_page_action)
test_actions.append(brex_openings_action)
test_actions.append(spotter_action)


test_action_plan = Div(
    Ol(
        *test_actions,
        id="action_plan_timeline",
        cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
    ),
    cls="container flex flex-col items-start gap-y-4 px-8",
)


@app.route("/")
def get():
    page_title = H1("Reefer", cls="text-4xl font-bold text-center")
    search_input = SearchInput(
        id="search_form",
        hx_post="/action_plan",
        hx_target="#openings_results",
        hx_swap="innerHTML",
    )
    results = Div(id="openings_results")

    return (
        Title("Reefer"),
        Main(
            Div(
                page_title,
                search_input,
                Div(
                    test_action_plan,
                    results,
                    cls="mx-auto w-full max-w-[1024px] flex flex-col items-center",
                ),
                cls="mx-auto py-10 flex flex-col items-center",
            ),
            cls="flex justify-center",
        ),
        Script(src=f"{flowurl}/flowbite.min.js"),
    )


agent = Agent()


async def timeline_event_generator(company: str):
    # for action in action_plan:
    #     yield to_xml(action)
    #     await asyncio.sleep(1.5)

    # -----------------------
    # TASK: FIND CAREERS PAGE
    # -----------------------
    find_careers_page_task = FindCareersPageTask(company=company)
    print("YIELDING: Initial FindCareersPageTask\n", to_xml(find_careers_page_task))
    yield to_xml(find_careers_page_task)
    await asyncio.sleep(0.01)

    careers_page_url = agent.perform_action(find_careers_page_task)
    print("Careers page URL: ", careers_page_url)
    assert careers_page_url is not None, "Careers page URL not found"
    print("YIELDING: Completed FindCareersPageTask", to_xml(find_careers_page_task))
    yield to_xml(find_careers_page_task)
    await asyncio.sleep(0.01)

    # -----------------------
    # TASK: FIND OPENINGS PAGE
    # -----------------------
    find_openings_page_task = FindOpeningsPageTask(
        careers_link=str(careers_page_url), company=company
    )
    print("YIELDING: Initial FindOpeningsPageTask\n", to_xml(find_openings_page_task))
    yield to_xml(find_openings_page_task)
    await asyncio.sleep(0.01)

    openings_page_url = agent.perform_action(find_openings_page_task)
    print("Openings page URL: ", openings_page_url)
    print("YIELDING: Completed FindCareersPageTask\n")
    yield to_xml(find_openings_page_task)
    await asyncio.sleep(0.01)

    # # -----------------------
    # # TASK: PARSE OPENINGS
    # # -----------------------
    parse_openings_task = ParseOpeningsTask(
        openings_link=str(openings_page_url),
        company=company,
        job_type="Software Engineer",
    )
    print("YIELDING: Initial ParseOpeningsTask\n")
    yield to_xml(parse_openings_task)
    await asyncio.sleep(0.1)

    openings = agent.perform_action(parse_openings_task)
    print("OPENINGS: ", openings)
    print("YIELDING: Completed ParseOpeningsTask\n")
    yield to_xml(parse_openings_task)
    await asyncio.sleep(0.01)


@app.post("/action_plan")
def fetch_action_plan(company: str):
    return None
    # return Div(
    #     Timeline(events=test_actions, id="action_plan_timeline", company=company),
    #     cls="container mx-10 mt-10 flex flex-col items-start gap-y-4",
    # )


@app.post("/stream_action_plan")
async def streaming_action_plan(
    company: str,
):
    async def event_stream():
        async for event in timeline_event_generator(company):
            yield event

    response = StreamingResponse(event_stream(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response
