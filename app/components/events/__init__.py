from abc import abstractmethod
from uuid import uuid4
from typing import Optional, TypeVar
from fasthtml.common import *
from enum import Enum

from .action_event import ActionEvent
from .contact_table_event import ContactTableEvent
from .parse_job_description_event import ParseJobDescriptionTask
from .parse_openings_task import ParseOpeningsTask
from .find_careers_page_task import FindCareersPageTask
from .find_openings_page_task import FindOpeningsPageTask
