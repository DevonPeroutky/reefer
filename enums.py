from enum import Enum


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
