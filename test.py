from fastcore.meta import test
from fasthtml.common import *
from typing import List

import asyncio
from starlette.responses import StreamingResponse

from data_types import JobOpening
from services.scraping_service import ScrapingService
from services.serp_service import SerpService

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"
hdrs = (
    # Flowbite CSS
    Link(href=f"{flowurl}/flowbite.min.css", rel="stylesheet"),
    Meta(name="theme-color", content="#ffffff"),
    # Tailwind CSS
    Script(src="https://cdn.tailwindcss.com"),
    # HTMX SSE extension
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.2/sse.js"),
)

extlink = Script(src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js")
htmxlink = Script(src="https://unpkg.com/htmx.org@1.9.12")
app = FastHTML(hdrs=(picolink, htmxlink, extlink), default_hdrs=False, live=True)


class Item:
    def __init__(self, name, id):
        self.id = id
        self.name = name

    def __ft__(self):
        return Li(
            f"Name: {self.name}",
            id=f"item-{self.id}",
            sse_swap=f"sse-item-{self.id}",
        )


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
            hx_post="/test_openings",
            hx_target="#openings_result",
            hx_swap="innerHTML",
            cls="flex",
        ),
        cls="container",
    )
    page = Main(hx_ext="chunked-transfer")(
        H1("transfer encoding chunked demo"),
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            # beforeend wasn't working as it seems like we're returning the whole thing each time.
            # hx_swap="beforeend",
            hx_swap="innerHTML",
        ),
        Ul(id="message"),
        Ul(id="openings"),
    )
    return Title("Chatbot Demo"), Main(form), page


items = [
    Item("John Doe", 1),
    Item("Jane Doe", 2),
    Item("Alice", 3),
    Item("Bob", 4),
    Item("Charlie", 5),
]


@app.get("/get-message")
async def get_message():
    async def event_stream():
        for item in items:
            item_html = to_xml(item)
            print("Sending item ", item_html)
            yield f"{item_html}"
            await asyncio.sleep(2)

    response = StreamingResponse(event_stream(), media_type="text/event-stream")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


# GOING FOR IT:
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
serp_api_key = os.getenv("SERPDOG_API_KEY")
assert anthropic_api_key, "ANTHROPIC_API_KEY environment variable must be set"
assert serp_api_key, "ANTHROPIC_API_KEY environment variable must be set"

scraping_service = ScrapingService(anthropic_api_key)
serp_service = SerpService(serp_api_key)


@app.post("/openings")
def get_openings(company: str, job_type: str):
    print(f"Getting {job_type} openings for {company}...")

    # Find careers page
    careers_page_url = serp_service.find_careers_url(company, job_type)
    openings_link = scraping_service.parse_openings_page_link_from_html(
        company=company, link=careers_page_url
    )
    assert openings_link, f"No openings page found for {company} at {careers_page_url}"
    print(f"Looking for {job_type} openings for {company} at {openings_link}")

    openings: List[JobOpening] = scraping_service.parse_openings_from_html(
        company=company, job_type=job_type, openings_link=openings_link
    )
    for opening in openings:
        opening.link = ScrapingService.resolve_url(openings_link, opening.link)
    print("OPENINGS", openings)

    return Ul(*openings)


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


@app.post("/test_openings")
def get_openings(company: str, job_type: str):
    for opening in test_openings:
        opening.link = ScrapingService.resolve_url(test_openings_url, opening.link)
    return Ul(*test_openings)


serve()
