from typing import Optional
from fasthtml.common import A, P, Li, Div
from dataclasses import dataclass


@dataclass
class JobOpening:
    id: str
    title: str
    location: Optional[str]
    link: str
    related: bool

    def __ft__(self):
        return Li(
            A(self.title, href=self.link, target="_blank"),
            P(self.location) if self.location else None,
            id=f"item-{self.id}",
            sse_swap=f"sse-item-{self.id}",
        )
