from typing import cast

from fasthtml.common import *

from starlette.responses import StreamingResponse
from app import JobOpening
from app.components.primitives.modal import (
    ModalBody,
)
from app.components.primitives.search_input import SearchInput
from app.components.application.timeline import Timeline
from app.custom_hdrs import CUSTOM_HDRS, FLOWBITE_INCLUDE_SCRIPT
from app.agent.agent import Agent
from app.services.serp_service import (
    DummySearchClient,
    ExaClient,
    SearchService,
    SerpDogClient,
    SerpService,
)
from app.stub.services import DummyScrapingService, DummySearchService

app = FastHTML(hdrs=CUSTOM_HDRS, ct_hdr=True, live=True)

# search_service = SerpService(search_client=DummySearchClient())
# agent = Agent(serp_service=search_service, scraping_service=DummyScrapingService())
serp_service = SerpService(search_client=SerpDogClient())
agent = Agent(serp_service=serp_service)


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
            ModalBody(
                title="Contact Details",
                body=Div("Old Content, this should be replaced with new content!"),
                id="details-modal",
            ),
            cls="flex justify-center py-12",
        ),
        FLOWBITE_INCLUDE_SCRIPT,
    )


@app.post("/action_plan")
def fetch_action_plan(company_name: str):
    timeline_id = "action_plan_timeline"
    return Div(
        Div(
            hx_post=f"/stream_action_plan?company_name={company_name}",
            hx_trigger="load",
            hx_target=f"#{timeline_id}",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Timeline(id=timeline_id, company_name=company_name),
    )


@app.post("/stream_action_plan")
async def streaming_action_plan(
    company_name: str,
):
    response = StreamingResponse(
        agent.find_company_information(company_name),
        media_type="text/html",
        headers={"X-Transfer-Encoding": "chunked"},
    )
    return response


@app.post("/research_jobs")
async def research_jobs(request: Request, company_name: str):
    # TODO: Don't do it this way
    form = await request.form()
    job_ids = cast(List[str], form.getlist("jobs[]"))

    response = StreamingResponse(
        agent.research_job_openings(job_ids),
        media_type="text/html",
        headers={"X-Transfer-Encoding": "chunked"},
    )
    return response


@app.post("/stream_contacts")
async def render_contact_table(request: Request, company_name: str):
    # TODO: Don't do it this way
    form = await request.form()

    response = StreamingResponse(
        agent.find_contacts(),
        media_type="text/html",
        headers={"X-Transfer-Encoding": "chunked"},
    )
    return response


@app.get("/modal")
def modal(job_id: str, contact_id: str):
    job: Optional[JobOpening] = agent.knowledge_service.get_job_opening(job_id)
    print(agent.knowledge_service.get_current_state().job_openings)
    print("Job: ", job)
    return Div(
        f"Job details for JOB {job.id if job else "unknown"}",
        hx_swap_oob="innerHTML:#details-modal-body",
        id="details-modal-body",
    )
