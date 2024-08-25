from fasthtml.common import *

from data_types import Contact


class ContactTable:
    def __init__(self, company: str, contacts: List[Contact], *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.company = company
        self.contacts = contacts

    def add_contact(self, contact: Contact):
        self.contacts.append(contact)

    def _render_contact_row(self, contact: Contact):
        return Tr(
            Th(
                contact.name,
                scope="row",
                cls="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white",
            ),
            Td(contact.job_title, cls="px-6 py-4"),
            Td(contact.location, cls="px-6 py-4"),
            Td(contact.email, cls="px-6 py-4"),
        )

    def __ft__(self):
        return Div(
            Table(
                Caption(
                    f"{self.company} Contacts",
                    cls="p-5 text-lg font-semibold text-left rtl:text-right text-gray-900 bg-white dark:text-white dark:bg-gray-800",
                ),
                Thead(
                    Tr(
                        Th("Name", scope="col", cls="px-6 py-3"),
                        Th("Title", scope="col", cls="px-6 py-3"),
                        Th("Notes", scope="col", cls="px-6 py-3"),
                        Th("Email", scope="col", cls="px-6 py-3"),
                    ),
                    cls="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400",
                ),
                Tbody(
                    Tr(
                        Th(
                            'Apple MacBook Pro 17"',
                            scope="row",
                            cls="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white",
                        ),
                        Td("Silver", cls="px-6 py-4"),
                        Td("Laptop", cls="px-6 py-4"),
                        Td("$2999", cls="px-6 py-4"),
                    ),
                    *[self._render_contact_row(contact) for contact in self.contacts],
                ),
                cls="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400",
            ),
            cls="relative overflow-x-auto shadow-md sm:rounded-lg",
        )
