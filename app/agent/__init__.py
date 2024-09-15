from typing import List, Optional
from pydantic import BaseModel

from app import Company, Contact, JobOpening
from app.stub.data import test_openings


class AgentState(BaseModel):
    company: Optional[Company] = None
    job_openings: List[JobOpening] = []
    desired_job_openings: List[JobOpening] = []
    contacts: List[Contact] = []
    desired_job_type: str = "Software Engineer"  # TODO: Don't hardcode this
