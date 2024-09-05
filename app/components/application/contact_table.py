from fasthtml.common import *
from typing import List, Tuple

from app.components.primitives.tag import CompanyTag
from app import Company, Contact, JobOpening


class ContactRow:
    def __init__(self, job_opening: JobOpening, contact: Contact):
        self.contact = contact
        self.job_opening = job_opening

    def __ft__(self):
        print("RENDERING CONTACT ROW: ", self.contact.name, " - ", self.contact.id)
        return Tr(
            Td(self.job_opening.title, cls="px-6 py-4"),
            Th(
                self.contact.name,
                scope="row",
                cls="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white",
            ),
            Td(self.contact.job_title, cls="px-6 py-4"),
            Td(self.contact.notes, cls="px-6 py-4"),
            Td(self.contact.email, cls="px-6 py-4"),
            id=self.contact.id,
        )


class ContactTable:
    def __init__(
        self,
        company: Company,
        job_contacts: List[Tuple[JobOpening, Contact]],
        *args,
        **kwargs
    ):
        self.args = args
        self.kwargs = kwargs
        self.company = company
        self.job_contacts = job_contacts

    def __ft__(self):
        return (
            Div(
                "Potential",
                CompanyTag(self.company.name.title()),
                "Contacts",
                cls="flex gap-x-2 py-5 text-lg font-semibold text-left rtl:text-right text-gray-900 bg-white dark:text-white dark:bg-gray-800",
            ),
            Table(
                Thead(
                    Tr(
                        Th("Job Opening", scope="col", cls="px-6 py-3"),
                        Th("Name", scope="col", cls="px-6 py-3"),
                        Th("Title", scope="col", cls="px-6 py-3"),
                        Th("Notes", scope="col", cls="px-6 py-3"),
                        Th("Email", scope="col", cls="px-6 py-3"),
                    ),
                    cls="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400",
                ),
                Tbody(
                    *[
                        ContactRow(job_opening=job, contact=contact)
                        for (job, contact) in self.job_contacts
                    ]
                ),
                cls="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400",
                # hx_post="/find_contacts",
                **self.kwargs,
            ),
        )
