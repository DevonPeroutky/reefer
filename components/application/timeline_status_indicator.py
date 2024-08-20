from fasthtml.common import *

from components.primitives.success_icon import SearchIcon
from components.primitives.spinner import Spinner
from components.primitives.success_icon import SuccessIcon

from enums import TaskStatus


class TimelineEventStatusIndicator:
    def __init__(self, status: TaskStatus, id: str):
        self.status = status
        self.id = id

    def __ft__(self):
        if self.status == TaskStatus.PENDING:
            return to_xml(
                SearchIcon(
                    id=f"{self.id}-loader",
                    cls="absolute flex items-center justify-center w-8 h-8 bg-gray-200 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900",
                )
            )
        elif self.status == TaskStatus.IN_PROGRESS:
            return to_xml(
                Spinner(
                    id=f"{self.id}-loader",
                    cls="absolute flex items-center justify-center w-8 h-8 bg-white rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900",
                )
            )
        elif self.status == TaskStatus.COMPLETED:
            return to_xml(SuccessIcon(id=f"{self.id}-loader"))
        else:
            return to_xml(SearchIcon(id=f"{self.id}-loader"))
