from fasthtml.common import *
from typing import List, Tuple

from app.components.primitives.link import Link
from app.components.primitives.tag import CompanyTag
from app import Company, Contact, JobOpening


class ContactRow:
    def __init__(self, job_opening: JobOpening, contact: Contact):
        self.contact = contact
        self.job_opening = job_opening

    def __ft__(self):
        return Tr(
            Td(
                Link(
                    self.job_opening.title.title(),
                    href=str(self.job_opening.link),
                    target="_blank",
                ),
                cls="px-6 py-4",
            ),
            Th(
                Link(
                    self.contact.name.title(),
                    href=str(self.contact.linkedin_url),
                    target="_blank",
                ),
                cls="px-6 py-4",
            ),
            Td(self.contact.job_title, cls="px-6 py-4"),
            Td(
                A('View details', href='#', type='button', data_modal_show='editUserModal', cls='font-medium text-blue-600 dark:text-blue-500 hover:underline'),
                cls="px-6 py-4"
            ),
            Td(
               self.contact.email,
               cls='px-6 py-4'
            ),
            id=self.contact.id,
        )


class ContactTable:
    def __init__(
        self,
        company: Company,
        job_contacts: List[Tuple[JobOpening, Contact]],
        *args,
        **kwargs,
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
                        Th("Details", scope="col", cls="px-6 py-3"),
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
                id="contacts-table",
                cls="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400",
                hx_post=f"/stream_contacts?company_name={self.company.name}",
                hx_trigger="load",
                hx_swap="beforeend",
                # hx_swap="innerHTML",
                hx_ext="chunked-transfer",
                **self.kwargs,
            ),
        )
