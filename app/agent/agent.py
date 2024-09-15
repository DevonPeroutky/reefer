import asyncio

from typing import List, Optional, AsyncGenerator, Any
from fasthtml.common import Safe, to_xml

from app import agent
from app.agent.knowledge_service import KnowledgeService
from app.components.application.contact_table import ContactRow
from app.components.events import FindCareersPageTask, ParseJobDescriptionTask
from app.components.events.find_contact_task import FindContactTask
from app.components.events.find_openings_page_task import FindOpeningsPageTask
from app.components.events.parse_openings_task import ParseOpeningsTask
from app.stub.data import spotter_openings, spotter
from app.agent import AgentState
from app.components.events.action_event import ActionEvent, StreamingActionEvent
from app.components.events.contact_table_event import ContactTableEvent
from app.components.primitives.success_icon import SuccessIcon
from app.actions.find_company_action import FindCompanyAction
from app.actions.parse_openings_action import ParseOpeningsAction
from app.actions.find_contacts_action import FindContactsAction
from app import Company, Contact, JobOpening
from app.actions.research_job_action import ResearchJobAction
from app.services.serp_service import SearchService, SerpService
from app.services.scraping_service import CareersPageScrapingService, ScrapingService
from app.utils.asyncio import combine_generators


"""
Finding contacts for a company is essentially a multi-step process of...

/find_company_information -> /parse_openings -> /research_job_openings -> /find_contacts




1. /find_company_information
    # FindCompanyAction
    a. Finding the company's career page
    b. Finding the page that lists the job openings (which may or may not be the same as the career page)

    # ParseOpeningsAction
    c. Parsing the job openings into a structured list of JobOpening's

2. /parse_openings
    # ResearchJobAction 
    a. Allow user to select which jobs they are interested in
    b. For each job, parse the job description to find relevant keywords and positions that can be used to find contacts

3. /find_contacts
    # FindContactsAction
    a. Use the keywords and positions to find linkedin profiles most relevant to each job opening
    b. Use getprospect API to find emails for each linkedin profile

"""


class Agent:
    def __init__(
        self,
        serp_service: Optional[SearchService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or CareersPageScrapingService()
        self.knowledge_service = KnowledgeService()
        self.render_queue = asyncio.Queue()

    async def execute_task(self, task: ActionEvent) -> AsyncGenerator[Safe, None]:
        # Send Pending Event to client immediately
        yield to_xml(task)
        await asyncio.sleep(0.0)

        # Execute Task
        await task.execute_task(self.knowledge_service.get_current_state())

        # Re-render completed event to client
        yield to_xml(task)
        await asyncio.sleep(0.0)

    async def execute_streaming_task(self, task: StreamingActionEvent):
        res = task.execute_streaming_task(self.knowledge_service.get_current_state())

        async for r in res:
            yield to_xml(r)
            await asyncio.sleep(0.0)

    async def execute_tasks_sequentially(self, tasks: List[ActionEvent]):
        for task in tasks:
            async for res in self.execute_task(task):
                yield res
                await asyncio.sleep(0.0)

    async def execute_tasks_in_parallel(self, tasks: List[ActionEvent]):
        async for res in combine_generators(
            *[self.execute_task(task) for task in tasks]
        ):
            yield res
            await asyncio.sleep(0.0)

    async def find_company_information(self, company_name: str):

        # Initialize the company
        current_state = self.knowledge_service.get_current_state()
        current_state.company = Company(
            name=company_name, careers_link=None, opening_link=None
        )

        # Execute tasks
        tasks = [
            FindCareersPageTask(
                serp_service=self.serp_service,
                knowledge_service=self.knowledge_service,
            ),
            FindOpeningsPageTask(
                scraping_service=self.scraping_service,
                knowledge_service=self.knowledge_service,
            ),
            ParseOpeningsTask(
                scraping_service=self.scraping_service,
                knowledge_service=self.knowledge_service,
            ),
        ]

        # Execute tasks sequentially
        for task in tasks:
            async for res in self.execute_task(task):
                yield res

    async def research_job_openings(self, job_ids: List[str]):
        agent_state = self.knowledge_service.get_current_state()
        assert (
            agent_state.company
        ), "Company must be set in the state before executing this task"
        agent_state.desired_job_openings = list(
            filter(lambda job: job.id in job_ids, agent_state.job_openings)
        )

        research_job_tasks = [
            ParseJobDescriptionTask(
                job=job,
                scraping_service=self.scraping_service,
                knowledge_service=self.knowledge_service,
            )
            for job in agent_state.desired_job_openings
        ]

        # Execute tasks concurrently and yield results as they complete
        async for res in combine_generators(
            *[self.execute_task(task) for task in research_job_tasks]
        ):
            yield res
            await asyncio.sleep(0)

        contact_table = ContactTableEvent(
            id="contact-table", company=agent_state.company, job_contacts=[]
        )
        yield to_xml(contact_table)

    # TODO: Move to a separate task
    async def find_contacts_for_opening(
        self, job_opening: JobOpening
    ) -> AsyncGenerator[str, None]:
        contacts: List[Contact] = await self.serp_service.find_list_of_contacts(
            job_opening.company, job_opening.keywords, job_opening.positions
        )
        print("---------" * 5)
        print("Found contacts: ", contacts)
        for contact_row in list(map(lambda c: ContactRow(job_opening, c), contacts)):
            yield to_xml(contact_row)
            await asyncio.sleep(1)

    async def find_contacts(self):
        agent_state = self.knowledge_service.get_current_state()
        assert (
            agent_state.desired_job_openings
        ), "Desired job openings must be set in the state before executing this task"

        tasks = [
            FindContactTask(
                job_opening=job,
                serp_service=self.serp_service,
                knowledge_service=self.knowledge_service,
            )
            for job in agent_state.desired_job_openings
        ]
        async for res in combine_generators(
            *[self.execute_streaming_task(task) for task in tasks]
        ):
            yield to_xml(res)
            await asyncio.sleep(0.0)

        yield to_xml(
            SuccessIcon(
                id=f"contact-table-loader",
                hx_swap_oob="outerHTML:#contact-table-loader",
            )
        )
        await asyncio.sleep(0.0)
