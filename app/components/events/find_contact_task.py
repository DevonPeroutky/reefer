import asyncio
from typing import AsyncGenerator, Optional
from app.components.events.action_event import ActionEvent, StreamingActionEvent
from app.services.serp_service import SearchService, SerpService
from app.agent import AgentState
from app.agent.knowledge_service import KnowledgeService
from app.components.primitives.tag import CompanyTag
from app import TaskStatus, TaskType
from fasthtml.common import *
from app import Company, JobOpening, Contact
from app.components.application.contact_table import ContactRow


class FindContactTask(StreamingActionEvent):

    def __init__(
        self,
        job_opening: JobOpening,
        knowledge_service: Optional[KnowledgeService] = None,
        serp_service: Optional[SearchService] = None,
        **kwargs,
    ):
        super().__init__(
            knowledge_service=knowledge_service,
            status=TaskStatus.IN_PROGRESS,
            task_type=TaskType.FIND_CAREERS_PAGE,
            **kwargs,
        )
        self.job_opening = job_opening
        self.contacts: List[Contact] = []
        self.serp_service: SearchService = serp_service or SerpService()

    async def execute_task(self, state: AgentState):
        contacts: List[Contact] = await self.serp_service.find_list_of_contacts(
            self.job_opening.company,
            self.job_opening.keywords,
            self.job_opening.positions,
        )
        print("---------" * 5)
        print("Found contacts: ", contacts)

        self.contacts = contacts
        # Is this thread safe????
        state.contacts.extend(contacts)

        super().complete_task()

    async def execute_streaming_task(
        self, state: AgentState
    ) -> AsyncGenerator[str, None]:
        contacts: List[Contact] = await self.serp_service.find_list_of_contacts(
            self.job_opening.company,
            self.job_opening.keywords,
            self.job_opening.positions,
        )
        print("---------" * 5)
        print("Found contacts: ", contacts)
        for contact_row in list(
            map(lambda c: ContactRow(self.job_opening, c), contacts)
        ):
            yield to_xml(contact_row)
            await asyncio.sleep(1)

    def __ft__(self):
        contact_rows = [
            ContactRow(self.job_opening, contact) for contact in self.contacts
        ]
        print("Contact Rows: ", [to_xml(row) for row in contact_rows])
        return contact_rows
