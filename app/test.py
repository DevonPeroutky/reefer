from fastcore.meta import test
from fasthtml.common import *
from typing import List

import asyncio
from starlette.responses import StreamingResponse

custom_script = Script(
    """
    console.log("Hello from custom script");
    htmx.logAll();
    """
)
extlink = Script(
    # src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js",
    # src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js",
    src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
)
# htmxlink = Script(src="https://unpkg.com/htmx.org@1.9.12")
app = FastHTML(hdrs=(picolink, extlink, custom_script), live=True)


@app.route("/")
def get():
    page = Main()(
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Button(
            "Get Message 2",
            hx_get="/get-message-2",
            hx_target="#message",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Ul(id="message", hx_ext="chunked-transfer"),
    )
    return (Title("Chatbot Demo"), page)


items = [
    Li("John Doe", id="item1"),
    Li("Steve", id="item2"),
    # Li("Alice", id="item1", hx_swap_oob="outerHTML"),  # Doesn't work
    Li("Jessica", id="item1", hx_swap_oob="true"),  # Doesn't work
    Li("Alice", id="item1", hx_swap_oob="true"),  # Doesn't work
    Li("Bob", id="4"),  # Successfully appended
]


@app.get("/get-message")
async def get_message():
    async def event_stream():
        for item in items:
            yield to_xml(item)
            await asyncio.sleep(1)

    # response = StreamingResponse(event_stream(), media_type="text/html")
    # response.headers["Transfer-Encoding"] = "chunked"
    # return response
    return StreamingResponse(
        event_stream(),
        media_type="text/html",
        headers={"Transfer-Encoding": "chunked"},
    )


@app.get("/get-message-2")
async def get_message_2():
    return StreamingResponse(
        to_xml(Li("Alice", id="item1", hx_swap_oob="true")),
        media_type="text/html",
        headers={"Transfer-Encoding": "chunked"},
    )
