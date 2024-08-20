import asyncio

from fasthtml.common import *
from starlette.responses import StreamingResponse

htmxlink = Script(
    src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js"
)
app = FastHTML(hdrs=(picolink, htmxlink), live=True)


class Item:
    def __init__(self, name, id):
        self.id = id
        self.name = name

    def __ft__(self):
        return Li(
            f"Name: {self.name}",
            id=f"item-{self.id}",
            sse_swap=f"sse-item-{self.id}",
            hx_swap_oob="true",
        )


items = [
    Item("AIN'T SHIT", 1),
    Item("Jane Doe", 2),
    Item("Alice", 1),
    Item("Bob", 4),
    Item("Charlie", 5),
    Item("Jane Doe", 2),
]


async def message_generator():
    for item in items:
        yield to_xml(item)
        await asyncio.sleep(0.5)


@app.route("/")
def get():
    page = Main(
        H1("transfer encoding chunked demo"),
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Div(Ul(to_xml(Item("BITCHES", 1)), id="message", cls="list-disc"), cls="mt-4"),
    )
    return Title("Chunked Transfer Demo"), page


@app.get("/get-message")
async def get_message():
    async def streaming_content():
        async for chunk in message_generator():
            yield chunk

    response = StreamingResponse(streaming_content(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


serve()
