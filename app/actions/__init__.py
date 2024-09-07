import asyncio

from enum import Enum
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, TypeVar, Generic
from fasthtml.common import Safe

T = TypeVar("T")


class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskType(Enum):
    FIND_CAREERS_PAGE = "find_careers_page"
    FIND_OPENINGS_PAGE = "find_openings_page"
    PARSE_OPENINGS = "parse_openings"
    FIND_CONTACTS = "find_contacts"
    PARSE_JOB_DESCRIPTION = "parse_job_description"


class BaseAction(ABC, Generic[T]):
    @abstractmethod
    async def yield_action_stream(self, *args, **kwargs):
        pass

    @abstractmethod
    def yield_action_result(self) -> T:
        pass

    async def yield_dummy_stream(self, items: List[T], schedule: List[int]):
        for item, delay in zip(items, schedule):
            await asyncio.sleep(delay)
            yield item
