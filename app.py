import asyncio
from asyncio.tasks import Task

from fasthtml.common import *

from starlette.responses import StreamingResponse
from components.primitives.search_input import SearchInput
from components.primitives.spinner import Spinner
from components.primitives.success_icon import SuccessIcon
from data_types import JobOpening, TaskStatus
from components.timeline import Timeline, TimelineEvent
from services.scraping_service import ScrapingService
from test import Item

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"

custom_script = Script(
    """
    // var form = document.getElementById('search_form');

    // Dispatch the custom event twice
    // form.dispatchEvent(new CustomEvent('customEvent'));
    // form.dispatchEvent(new CustomEvent('customEvent'));


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
    # HTMX SSE extension
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.2/sse.js"),
    # HTMX
    Script(src="https://unpkg.com/htmx.org@1.9.12"),
    # Ext
    Script(src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js"),
    custom_styles,
    custom_script,
)

app = FastHTML(hdrs=hdrs, default_hdrs=False)

test_openings = [
    JobOpening(
        id="0",
        title="Compliance Manager",
        location=None,
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
        location=None,
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


@app.route("/")
def get():
    page_title = H1("Reefer", cls="text-4xl font-bold text-center")
    search_input = SearchInput(
        id="search_form",
        hx_post="/action_plan",
        hx_target="#openings_results",
        hx_swap="innerHTML",
    )

    loader = Spinner(
        id="loader",
        cls="htmx-indicator transition-opacity duration-500 ease-in",
    )

    # results = Div(
    #     H1("Action Plan", cls="text-2xl font-bold text-center mt-10"),
    #     Timeline(events=[], id="openings_results"),
    #     loader,
    #     cls="container mx-10 mt-10 flex flex-col items-start gap-y-4",
    # )
    results = Div(id="openings_results")

    return (
        Title("Reefer"),
        Main(
            Div(
                page_title,
                search_input,
                results,
                cls="container mx-auto, mt-10 flex flex-col items-center",
            ),
        ),
        Script(src=f"{flowurl}/flowbite.min.js"),
    )


initial_action_plan = [
    TimelineEvent(
        id=1,
        title="Find page containing the list of openings at Company",
        status=TaskStatus.IN_PROGRESS,
        task_type="Task",
    ),
]

action_plan = [
    TimelineEvent(
        id=1,
        title="Find page containing the list of openings at Company",
        status=TaskStatus.COMPLETED,
        task_type="Task",
        hx_swap_oob="true",
    ),
    TimelineEvent(
        id=2,
        title="Parsing and filtering openings",
        status=TaskStatus.IN_PROGRESS,
        task_type="Task",
        # hx_swap_oob="true",
    ),
    # TimelineEvent(
    #     id=2,
    #     title="(UPDATED) Parsing and filtering openings",
    #     status=TaskStatus.COMPLETED,
    #     task_type="Task",
    #     hx_swap_oob="true",
    # ),
    TimelineEvent(
        id=3,
        title="Finding relevant contacts at Company",
        status=TaskStatus.PENDING,
        task_type="Task",
    ),
    TimelineEvent(
        id=3,
        title="Finding relevant contacts at Company",
        status=TaskStatus.COMPLETED,
        task_type="Task",
        hx_swap_oob="true",
    ),
    TimelineEvent(
        id=4,
        title="Find page containing the list of openings at Company",
        status=TaskStatus.PENDING,
        task_type="Task",
    ),
    TimelineEvent(
        id=4,
        title="Find page containing the list of openings at Company",
        status=TaskStatus.COMPLETED,
        task_type="Task",
        hx_swap_oob="true",
    ),
]


async def timeline_event_generator():
    print("HERE!")
    await asyncio.sleep(1.5)
    for action in action_plan[:3]:
        yield to_xml(action)
        await asyncio.sleep(1.5)


@app.post("/action_plan")
def fetch_action_plan():
    return Div(
        Timeline(events=initial_action_plan, id="action_plan_timeline"),
        cls="container mx-10 mt-10 flex flex-col items-start gap-y-4",
    )


@app.post("/stream_action_plan")
async def streaming_action_plan():
    async def event_stream():
        async for event in timeline_event_generator():
            print("YIelding ", event)
            yield event

    response = StreamingResponse(event_stream(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response
