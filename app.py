from typing import cast

from fasthtml.common import *

from starlette.responses import StreamingResponse
from components.primitives.search_input import SearchInput
from components.application.contact_table import ContactTable
from components.application.timeline import Timeline
from custom_hdrs import CUSTOM_HDRS, FLOWBITE_INCLUDE_SCRIPT
from services.action_planner import Agent

app = FastHTML(hdrs=CUSTOM_HDRS, live=True)

agent = Agent()


@app.route("/")
def get():
    page_title = H1("Reefer", cls="text-4xl font-bold text-center")
    search_input = SearchInput(
        id="search_form",
        hx_post="/action_plan",
        hx_target="#openings_results",
        hx_swap="innerHTML",
    )
    results = Div(
        id="openings_results",
        cls="mx-auto w-full max-w-[1024px] flex flex-col items-start w-[1024px]",
    )

    return (
        Title("Reefer"),
        Main(
            Div(
                page_title,
                search_input,
                results,
            ),
            cls="flex justify-center",
        ),
        FLOWBITE_INCLUDE_SCRIPT,
    )


@app.post("/action_plan")
def fetch_action_plan(company_name: str):
    return Timeline(events=[], id="action_plan_timeline", company_name=company_name)


@app.post("/contacts_table")
async def render_contact_table(request: Request, company_name: str):
    # TODO: Don't do it this way
    form = await request.form()
    print("Form: ", form)
    job_ids = cast(List[str], form.getlist("jobs[]"))
    print("JOBS IDs: ", job_ids)

    response = StreamingResponse(agent.find_contacts(job_ids), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.post("/stream_contacts")
async def stream_contacts(request: Request):
    # TODO: Don't do it this way
    form = await request.form()
    print("Form: ", form)
    job_ids = cast(List[str], form.getlist("jobs[]"))
    print("JOBS IDs: ", job_ids)

    response = StreamingResponse(agent.find_contacts(job_ids), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.post("/stream_action_plan")
async def streaming_action_plan(
    company_name: str,
):
    response = StreamingResponse(
        agent.find_company_information(company_name), media_type="text/html"
    )
    response.headers["Transfer-Encoding"] = "chunked"
    return response
