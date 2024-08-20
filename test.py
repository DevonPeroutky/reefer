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
    page = Main(hx_ext="chunked-transfer")(
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            # beforeend wasn't working as it seems like we're returning the whole thing each time.
            # hx_swap="beforeend",
            hx_swap="innerHTML",
        ),
        Ul(id="message"),
    )
    return (Title("Chatbot Demo"), page)


items = [
    Item("John Doe", 1),
    Item("Jane Doe", 2),
    Item("Alice", 1),
    Item("Bob", 4),
    Item("Charlie", 5),
    Item("Jane Doe", 2),
]


@app.get("/get-message-reference")
async def get_message_reference():
    async def event_stream():
        for item in items:
            item_html = to_xml(item)
            print("Sending item ", item_html)
            yield f"{item_html}"
            await asyncio.sleep(1)

    response = StreamingResponse(event_stream(), media_type="text/event-stream")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.get("/get-message")
async def get_message():
    async def event_stream():
        for item in items:
            item_html = to_xml(item)
            print("Sending item ", item_html)
            yield f"{item_html}"
            await asyncio.sleep(1)

    response = StreamingResponse(event_stream(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response
