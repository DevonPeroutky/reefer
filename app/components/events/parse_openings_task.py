import fasthtml.svg as svg

from app.agent import AgentState
from app.agent.knowledge_service import KnowledgeService
from app.components.events import TimelineActionEvent
from app.components.primitives.tag import CompanyTag, JobTypeTag, OutputInputTag
from app import TaskStatus, TaskType
from fasthtml.common import *
from itertools import groupby as itertools_groupby

from app.services.scraping_service import CareersPageScrapingService, ScrapingService


class ParseOpeningsTask(TimelineActionEvent):
    def __init__(
        self,
        knowledge_service: Optional[KnowledgeService] = None,
        scraping_service: Optional[ScrapingService] = None,
        **kwargs,
    ):
        super().__init__(
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.PARSE_OPENINGS,
            knowledge_service=knowledge_service,
            **kwargs,
        )
        self.scraping_service = scraping_service or CareersPageScrapingService()

    async def execute_timeline_task(self, state: AgentState):
        assert (
            state.company
        ), "Company must be set in the state before executing this task"

        job_openings = await self.scraping_service.parse_openings_from_link(
            company=state.company,
            job_type=state.desired_job_type,
        )
        state.job_openings = job_openings

    def _render_title(self):
        agent_state = self.get_current_state()
        assert agent_state.company, "Company must be set before rendering the title"

        title_cls = "flex gap-x-2 font-medium leading-tight"
        if self.status == TaskStatus.IN_PROGRESS:
            title_cls += " italic"

        return H3(
            Span("Parsing "),
            OutputInputTag(
                A(
                    agent_state.company.opening_link,
                    href=str(agent_state.company.opening_link),
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                )
            ),
            Span("for"),
            JobTypeTag(agent_state.desired_job_type),
            "openings at",
            CompanyTag(agent_state.company.name.title()),
            cls=title_cls,
        )

    def _render_details(self):
        agent_state = self.get_current_state()
        assert agent_state.company, "Company must be set before rendering the details"

        sorted_by_location = sorted(
            agent_state.job_openings or [],
            key=lambda x: x.location or "Unknown",
            reverse=True,
        )
        grouped_by_location = itertools_groupby(
            sorted_by_location,
            lambda x: x.location or "Unknown",
        )

        openings_by_locations = [
            Div(
                H3(location, cls="font-medium text-lg mt-4 mb-2"),
                Ul(*list(openings), cls="list-disc list-inside"),
            )
            for location, openings in grouped_by_location
        ]

        return (
            Div(
                f"Found {agent_state.desired_job_type} jobs in the following locations... ",
                Form(
                    Div(*openings_by_locations),
                    Div(
                        Button(
                            "Find Contacts",
                            svg.Svg(
                                svg.Path(
                                    stroke="currentColor",
                                    stroke_linecap="round",
                                    stroke_linejoin="round",
                                    stroke_width="2",
                                    d="M1 5h12m0 0L9 1m4 4L9 9",
                                ),
                                aria_hidden="true",
                                xmlns="http://www.w3.org/2000/svg",
                                fill="none",
                                viewbox="0 0 14 10",
                                cls="rtl:rotate-180 w-3.5 h-3.5 ms-2",
                            ),
                            type="submit",
                            cls="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
                        ),
                        cls="flex font-medium gap-x-2 mt-8",
                    ),
                    # hx_post=f"/contacts_table?company_name={self.company.name}",
                    hx_post=f"/research_jobs?company_name={agent_state.company.name}",
                    hx_target="#action_plan_timeline",
                    hx_swap="beforeend",
                    hx_ext="chunked-transfer",
                ),
            )
            if agent_state.job_openings
            else None
        )
