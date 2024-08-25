from typing import cast

from fasthtml.common import *

from starlette.responses import StreamingResponse
from components.primitives.search_input import SearchInput
from actions.events import (
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
)
from components.application.contact_table import ContactTable
from components.application.timeline import Timeline
from custom_hdrs import CUSTOM_HDRS, FLOWBITE_INCLUDE_SCRIPT
from services.action_planner import Agent

app = FastHTML(hdrs=CUSTOM_HDRS, live=True)


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
    test_results_table = Ol(id="test_results_table")

    return (
        Title("Reefer"),
        Main(
            Div(
                page_title,
                search_input,
                Div(
                    # TEST_ACTION_PLAN,
                    results,
                    test_results_table,
                    cls="mx-auto w-full max-w-[1024px] flex flex-col items-start w-[1024px]",
                ),
                cls="mx-auto py-10 flex flex-col items-center w-full",
            ),
            cls="flex justify-center",
        ),
        FLOWBITE_INCLUDE_SCRIPT,
    )


agent = Agent()


@app.post("/action_plan")
def fetch_action_plan(company_name: str):
    return Div(
        Timeline(events=[], id="action_plan_timeline", company_name=company_name),
        cls="container mx-10 mt-10 flex flex-col items-start gap-y-4",
    )


@app.post("/find_contacts")
async def find_contacts(request: Request, company: str):
    # TODO: Don't do it this way
    form = await request.form()
    print("Form: ", form)
    jobs = cast(List[str], form.getlist("jobs[]"))
    print("JOBS: ", jobs)

    async def event_stream():
        for job in jobs:
            yield to_xml(Div("hi"))

    response = StreamingResponse(event_stream(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.post("/stream_action_plan")
async def streaming_action_plan(
    company_name: str,
):
    response = StreamingResponse(
        agent.test_timeline_event_generator(company_name), media_type="text/html"
    )
    response.headers["Transfer-Encoding"] = "chunked"
    return response
