from fasthtml.common import *

import asyncio
from starlette.responses import StreamingResponse

from app.custom_hdrs import FLOWBITE_INCLUDE_SCRIPT

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"
custom_script = Script(
    """

    document.addEventListener('DOMContentLoaded', function() {
        console.log("Adding htmx event listeners");
        document.body.addEventListener('htmx:configRequest', function(evt) {
            evt.detail.headers['HX-Debug'] = 'true';
        });

        document.body.addEventListener("htmx:beforeSwap", (event) => {
            console.log("HTMX beforeSwap event fired:", event.detail);
            // event.detail.shouldSwap = true;
        });

        document.body.addEventListener('htmx:afterSwap', (event) => {
            // console.log('Chunk received and swapped into the DOM:', event);

            // Access the target element and the swapped content
            const chunkContent = event.detail.elt; // The element that received the chunk

            // Run your custom JavaScript here upon each chunk received
            reinitializeFlowbiteOnNewModals(chunkContent);
        });

        function reinitializeFlowbiteOnNewModals(chunkContent) {

            // Check if the chunk contains an element with a specific data attribute, e.g., data-flowbite-init
            const flowbiteElement = chunkContent.querySelector('[data-modal-target]');

            // Call initFlowbite if the element with the data attribute is found
            if (flowbiteElement) {

                const start = performance.now();
                initFlowbite();
                const end = performance.now();
                console.log('!!!!!!!!!!!!! Flowbite re-initialized in ' + (end - start) + ' milliseconds.');
            }
        }

        document.body.addEventListener("htmx:swapError", (event) => {
            console.log("HTMX swapError event fired:", event.detail);
        });
    });
    """
)

CUSTOM_HDRS = (
    # Flowbite CSS
    Link(
        href=f"{flowurl}/dist/flowbite.min.css",
        rel="stylesheet",
    ),
    Meta(name="theme-color", content="#ffffff"),
    # Tailwind CSS
    Script(src="https://cdn.tailwindcss.com"),
    custom_script,
)
app = FastHTML(hdrs=CUSTOM_HDRS, ct_hdr=True, live=True)


class ModalButton:

    def __init__(self, text: str, **kwargs):
        self.kwargs = kwargs
        self.text = text

    def __ft__(self):
        return A(
            self.text,
            type="button",
            cls="font-medium text-blue-600 dark:text-blue-500 hover:underline",
            **self.kwargs,
        )


class ModalBody:

    def __init__(self, title: str, body: Any, id: str, **kwargs):
        self.title = title
        self.body = body
        self.id = id
        self.kwargs = kwargs

    def __ft__(self):
        return Div(
            Div(
                Div(
                    Div(
                        H3(
                            self.title,
                            cls="text-xl font-semibold text-gray-900 dark:text-white",
                        ),
                        cls="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600",
                    ),
                    Div(
                        *self.body,
                        id=f"{self.id}-body",
                        cls="p-4 md:p-5 space-y-4",
                    ),
                    Div(
                        Button(
                            "I accept",
                            data_modal_hide=self.id,
                            type="button",
                            cls="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
                        ),
                        Button(
                            "Decline",
                            data_modal_hide=self.id,
                            type="button",
                            cls="py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
                        ),
                        cls="flex items-center p-4 md:p-5 border-t border-gray-200 rounded-b dark:border-gray-600",
                    ),
                    cls="relative bg-white rounded-lg shadow dark:bg-gray-700",
                ),
                cls="relative p-4 w-full max-w-2xl max-h-full",
            ),
            id=f"{self.id}",
            hx_debug="true",
            data_modal_backdrop="static",
            tabindex="-1",
            aria_hidden="true",
            cls="hidden overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full",
        )


@app.route("/")
def get():

    page = Main()(
        Div(
            H1("Non-working modal example"),
            Div(
                hx_get="/get-model-via-chunk",
                hx_trigger="load",
                # Uncommenting this will make the modal work
                # hx_target="#non-working-modal",
                hx_swap="beforeend",
                hx_ext="chunked-transfer",
                **{
                    "hx-on:htmx:after-swap": "console.log('REINITIALIZING FLOWBIT'); initFlowbite();"
                },
            ),
        ),
        Div(
            Div(id="non-working-modal"),
        ),
        Script(src=f"{flowurl}/flowbite.min.js"),
        cls="p-4",
    )
    return (Title("Demo"), page)


modal_items = [
    ModalBody(
        title="Contact Details",
        body=Div("Old Content, this should be replaced with new content!"),
        id="details-modal",
    ),
    ModalButton(
        text="View Modal",
        hx_get="/modal-content",
        data_modal_target="details-modal",
        data_modal_show="details-modal",
        hx_trigger="click",
        hx_swap="none",
    ),
]


@app.get("/get-model-via-chunk")
async def get_message():
    async def event_stream():
        for item in modal_items:
            yield to_xml(item)
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/html",
        headers={"X-Transfer-Encoding": "chunked"},
    )


@app.get("/modal-content")
def modal():
    return Div(
        "NEW CONTENT",
        hx_swap_oob="innerHTML:#details-modal-body",
        id="details-modal-body",
    )
