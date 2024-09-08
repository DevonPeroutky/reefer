from typing import cast

from fasthtml.common import *

from starlette.responses import StreamingResponse
from app import JobOpening
from app.components.primitives.modal import (
    ModalBody,
    ModalButton,
)
from app.components.primitives.search_input import SearchInput
from app.components.application.contact_table import ContactTable
from app.components.application.timeline import Timeline
from app.services.action_planner import Agent
from app.custom_hdrs import CUSTOM_HDRS, FLOWBITE_INCLUDE_SCRIPT
from app.services.scraping_service import DummyScrapingService
from app.services.serp_service import DummySearchService

app = FastHTML(hdrs=CUSTOM_HDRS, live=True)

agent = Agent(
    serp_service=DummySearchService(), scraping_service=DummyScrapingService()
)


@app.route("/")
def get():
    page_title = H1("Reefer", cls="mt-12 text-4xl font-bold text-center")
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
            Div("SUCK THIS", id="fuck_me"),
            ModalBody(
                title="Contact Details",
                body=Div("REPLACE THIS BODY????"),
                id="details-modal",
            ),
            cls="flex justify-center py-12",
        ),
        FLOWBITE_INCLUDE_SCRIPT,
    )


@app.post("/action_plan")
def fetch_action_plan(company_name: str):
    return Div(
        ModalButton(
            text="View Details",
            hx_get=f"/modal?job_id={0}&contact_id={1}",
            data_modal_target="details-modal",
            data_modal_show="details-modal",
            hx_swap="innerHTML",
            hx_target="#details-modal-body",
            hx_trigger="click",
        ),
        Timeline(events=[], id="action_plan_timeline", company_name=company_name),
        ModalButton(
            text="View Details",
            hx_get=f"/modal?job_id={0}&contact_id={1}",
            data_modal_target="details-modal",
            data_modal_show="details-modal",
            hx_swap="innerHTML",
            hx_target="#details-modal-body",
            hx_trigger="click",
        ),
    )


@app.post("/stream_action_plan")
async def streaming_action_plan(
    company_name: str,
):
    response = StreamingResponse(
        agent.find_company_information(company_name), media_type="text/html"
    )
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.post("/research_jobs")
async def research_jobs(request: Request, company_name: str):
    # TODO: Don't do it this way
    form = await request.form()
    job_ids = cast(List[str], form.getlist("jobs[]"))

    print("Finding information for jobs: ", job_ids)
    response = StreamingResponse(
        agent.research_job_openings(job_ids), media_type="text/html"
    )
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.post("/stream_contacts")
async def render_contact_table(request: Request, company_name: str):
    # TODO: Don't do it this way
    form = await request.form()
    job_ids = cast(List[str], form.getlist("jobs[]"))
    print(agent)
    print(agent.openings)

    print("Finding contacts for jobs: ", job_ids)
    response = StreamingResponse(
        agent.find_contacts(agent.desired_job_openings), media_type="text/html"
    )
    response.headers["Transfer-Encoding"] = "chunked"
    return response


@app.get("/modal")
def modal(job_id: str, contact_id: str):
    job: Optional[JobOpening] = agent.get_job_opening(job_id)
    return Div(
        "Job details for JOB",
        id="details-modal-body",
        hx_debug="true",
    )
    # return ModalBody(
    #     title="Contact Details",
    #     body=Div(
    #         "Job details for {} - {}".format(
    #             job.title if job else "Unknown", contact_id
    #         ),
    #         id="contact-details-modal-body",
    #     ),
    #     id="details-modal",
    # )
