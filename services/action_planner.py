from asyncio import create_task
from data_types import (
    ActionEvent,
    FindCareersPageTask,
    FindOpeningsPageTask,
    ParseOpeningsTask,
    TaskStatus,
    TaskType,
)
from components.timeline import Timeline
from services.serp_service import SerpService
from services.scraping_service import ScrapingService
from typing import List, Optional, cast


class Agent:
    def __init__(
        self,
        serp_service: Optional[SerpService] = None,
        scraping_service: Optional[ScrapingService] = None,
    ):
        self.serp_service = serp_service or SerpService()
        self.scraping_service = scraping_service or ScrapingService()

    def perform_action(self, task: ActionEvent):
        match (task.task_type):
            case TaskType.FIND_CAREERS_PAGE:
                task = cast(FindCareersPageTask, task)
                careers_link = self.serp_service.find_careers_url(task.company)
                task.complete_task(link=careers_link)
                return careers_link
            case TaskType.FIND_OPENINGS_PAGE:
                task = cast(FindOpeningsPageTask, task)
                openings_link = (
                    self.scraping_service.find_openings_page_link(
                        link=task.careers_link, company=task.company
                    )
                    or task.careers_link
                )
                task.complete_task(openings_link=openings_link)
                return openings_link
            case TaskType.PARSE_OPENINGS:
                task = cast(ParseOpeningsTask, task)
                assert task and task.openings_link, "Openings link not found"
                openings = self.scraping_service.parse_openings_from_link(
                    openings_link=task.openings_link,
                    company=task.company,
                    job_type=task.job_type,
                )
                task.complete_task(openings=openings)
                return openings
