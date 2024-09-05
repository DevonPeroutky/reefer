import asyncio

from fasthtml.common import *
from starlette.responses import StreamingResponse

from services.scraping_service import ScrapingService

htmxlink = Script(src="https://unpkg.com/htmx.org@1.9.12")
extlink = Script(
    # src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js",
    src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js",
)
app = FastHTML(hdrs=(picolink, htmxlink, extlink), live=True, default_hdrs=False)


class Item:
    def __init__(self, name, id):
        self.id = id
        self.name = name

    def __ft__(self):
        return Li(
            f"Name: {self.name}",
            id=f"item-{self.id}",
            sse_swap=f"sse-item-{self.id}",
            # hx_swap_oob="true",
        )


items = [
    Item("AIN'T SHIT", 1),
    Item("Jane Doe", 2),
    Item("Alice", 1),
    Item("Bob", 4),
    Item("Charlie", 5),
    Item("Jane Doe", 2),
]


scraping_service = ScrapingService()


async def message_generator():
    for item in items:
        yield to_xml(item)
        await asyncio.sleep(1)


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


@app.get("/get-message")
async def get_message():
    async def event_stream():
        for item in items:
            item_html = to_xml(item)
            print("Sending item ", item_html)
            yield item_html
            await asyncio.sleep(1)

    response = StreamingResponse(event_stream(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


serve()
