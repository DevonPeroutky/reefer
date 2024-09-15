from typing import Optional
from app import JobOpening
from app.agent import AgentState


class KnowledgeService:
    def __init__(self):
        self.knowledge = AgentState()

    def get_current_state(self) -> AgentState:
        return self.knowledge

    def upsert_job_opening(self, job_opening):
        other_jobs = list(
            filter(lambda job: job.id != job_opening.id, self.knowledge.job_openings)
        )

        self.knowledge.job_openings = other_jobs + [job_opening]

    def get_job_opening(self, job_id: str) -> Optional[JobOpening]:
        openings = self.get_current_state().job_openings
        return next(filter(lambda job: job.id == job_id, openings), None)
