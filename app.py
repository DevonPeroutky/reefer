import asyncio

from fasthtml.common import *

from starlette.responses import StreamingResponse
from components.primitives.search_input import SearchInput
from data_types import JobOpening
from services.scraping_service import ScrapingService
from test import Item

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"
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
)

app = FastHTML(hdrs=hdrs, default_hdrs=False)

test_openings_url = "https://www.brex.com/careers"
test_openings = [
    JobOpening(
        id="0",
        title="Compliance Manager",
        location=None,
        link="/careers#Compliance-heading",
        related=False,
    ),
    JobOpening(
        id="1",
        title="Data Scientist",
        location=None,
        link="/careers#Data-heading",
        related=True,
    ),
    JobOpening(
        id="2",
        title="Designer",
        location=None,
        link="/careers#Design-heading",
        related=False,
    ),
    JobOpening(
        id="3",
        title="Software Engineer",
        location=None,
        link="/careers#Engineering-heading",
        related=True,
    ),
    JobOpening(
        id="4",
        title="Financial Analyst",
        location=None,
        link="/careers#Finance-heading",
        related=False,
    ),
    JobOpening(
        id="5",
        title="Legal Counsel",
        location=None,
        link="/careers#Legal-heading",
        related=False,
    ),
    JobOpening(
        id="6",
        title="Marketing Manager",
        location=None,
        link="/careers#Marketing-heading",
        related=False,
    ),
    JobOpening(
        id="7",
        title="Operations Specialist",
        location=None,
        link="/careers#Operations-heading",
        related=False,
    ),
    JobOpening(
        id="8",
        title="Administrative Assistant",
        location=None,
        link="/careers#Other General and Administrative-heading",
        related=False,
    ),
    JobOpening(
        id="9",
        title="HR Specialist",
        location=None,
        link="/careers#People-heading",
        related=False,
    ),
    JobOpening(
        id="10",
        title="Sales Representative",
        location=None,
        link="/careers#Sales-heading",
        related=False,
    ),
]


@app.route("/")
def get():
    form = Div(
        Form(
            Input(type="text", name="company", placeholder="Company", id="company"),
            Input(type="text", name="job_type", placeholder="Role", id="job_type"),
            Button(
                "Get Openings",
                type="submit",
            ),
            Div(id="openings_result"),
            hx_post="/stream_events",
            hx_target="#openings_result",
            hx_swap="innerHTML",
            cls="flex",
        ),
        cls="container mx-auto flex justify-center mt-10",
    )
    page_title = H1("Reefer", cls="text-4xl font-bold text-center")
    search_input = SearchInput(
        hx_post="/stream_events", hx_target="#openings_results", hx_swap="innerHTML"
    )
    results = Div(id="openings_results")
    return (
        Title("Reefer"),
        Main(
            Div(
                page_title, search_input, form, results, cls="container mx-auto, mt-10"
            ),
            Ul(id="openings_results"),
            hx_ext="chunked-transfer",
        ),
        Script(src=f"{flowurl}/flowbite.min.js"),
    )


@app.post("/test_openings")
def get_openings(company: str):
    print("Company:", company)
    for opening in test_openings:
        opening.link = ScrapingService.resolve_url(test_openings_url, opening.link)
    return Ul(*test_openings)


items = [
    Item("John Doe", 1),
    Item("Jane Doe", 2),
    Item("Alice", 3),
    Item("Bob", 4),
    Item("Charlie", 5),
]


@app.post("/stream_events")
def stream_openings():
    async def event_stream():
        for item in test_openings:
            item_html = to_xml(item)
            print("Sending item ", item_html)
            yield f"{item_html}"
            # yield item
            await asyncio.sleep(2)

    response = StreamingResponse(event_stream(), media_type="text/event-stream")
    # response.headers["Transfer-Encoding"] = "chunked"
    return response
