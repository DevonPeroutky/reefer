from fasthtml.common import *
from starlette.responses import StreamingResponse
import asyncio

# Set up the app, including daisyui and tailwind for the chat component
hdrs = (
    picolink,
    Script(src="https://cdn.tailwindcss.com"),
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
    ),
    Script(src="https://unpkg.com/htmx-ext-debug@2.0.0/debug.js"),
)

app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto", live=True, debug=True)


@app.route("/")
def get():
    page = Main(hx_ext="chunked-transfer")(
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            hx_swap="innerHTML",
            hx_ext="chunked-transfer",
        ),
        Button(
            "Get Message 2",
            hx_get="/get-message-2",
            hx_target="#message",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Ul(
            id="message",
        ),
    )
    return (Title("Demo"), page)


items = [
    Li("John Doe", id=1),
    Li("Alice", id=1, hx_swap_oob="outerHTML"),  # Doesn't update
    Li("Bob", id=4),  # Successfully appended
]


@app.get("/get-message")
async def get_message():
    async def event_stream():
        for item in items:
            yield to_xml(item)
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"X-Transfer-Encoding": "chunked", "Transfer-Encoding": "chunked"},
    )


@app.get("/get-message-2")
async def get_message_2():

    return StreamingResponse(
        to_xml(Li("Alice", id=1, hx_swap_oob="true")),
        media_type="text/html",
        headers={"Transfer-Encoding": "chunked"},
    )


serve()
