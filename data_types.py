from uuid import uuid4
from dataclasses import dataclass, field
from typing import Optional
from fasthtml.common import Div, Input, Label, A, P


@dataclass
class Company:
    name: str
    opening_link: Optional[str]
    careers_link: Optional[str]
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class JobOpening:
    id: str
    title: str
    company: Company
    location: Optional[str]
    link: str
    related: bool

    def __ft__(self):
        location = P(
            " (" + self.location + ")" if self.location else "",
        )
        return Div(
            Input(
                id="default-checkbox",
                type="checkbox",
                name="jobs[]",
                value=f"item-{self.id}",
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
            id=f"item-{self.id}",
        )


@dataclass
class Contact:
    name: str
    email: Optional[str]
    job_title: Optional[str]
    location: Optional[str]
    id: str = field(default_factory=lambda: str(uuid4()))

    def __ft__(self):
        return Div(
            P(
                self.name,
                " - ",
                self.job_title,
                " - ",
                self.location,
                " - ",
                self.email,
            ),
            cls="flex items-center mb-2",
            id=f"item-{self.id}",
        )
