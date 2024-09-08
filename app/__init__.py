from uuid import uuid4
from dataclasses import dataclass, field
from typing import List, Optional
from fasthtml.common import Div, Input, Label, A, P


@dataclass
class Company:
    name: str
    opening_link: Optional[str]
    careers_link: Optional[str]
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class JobOpening:
    title: str
    company: Company
    location: Optional[str]
    link: str
    related: bool
    id: str = field(default_factory=lambda: str(uuid4()))
    keywords: List[str] = field(default_factory=list)
    positions: List[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.title} ({self.link})"

    def __ft__(self):
        location = P(
            " (" + self.location + ")" if self.location else "",
        )
        return Div(
            Input(
                id="default-checkbox",
                type="checkbox",
                name="jobs[]",
                value=self.id,
                cls="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            ),
            Label(
                A(
                    self.title,
                    href=self.link,
                    target="_blank",
                    cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
                ),
                fr="default-checkbox",
                cls="ms-2 font-medium text-gray-900 dark:text-gray-300",
            ),
            cls="flex items-center mb-2",
            id=f"opening-{self.id}",
        )


@dataclass
class Contact:
    name: str
    company: Company
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))
