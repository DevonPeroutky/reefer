import fasthtml.svg as svg
from fasthtml.common import *
from uuid import uuid4 as uuid


class ModalButton:

    def __init__(self, text: str, **kwargs):
        self.kwargs = kwargs
        self.text = text

    def __ft__(self):
        return A(
            self.text,
            type="button",
            cls="font-medium text-blue-600 dark:text-blue-500 hover:underline",
            **self.kwargs,
        )
        # return A(
        #     self.text,
        #     # data_bs_toggle="modal",
        #     # data_bs_target=f"#{self.target}",
        #     # data_modal_target=self.target,
        #     # data_modal_show=self.target,
        #     type="button",
        #     cls="block text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        #     **self.kwargs,
        # )


class ModalBody:

    def __init__(self, title: str, body: Any, id: str, **kwargs):
        self.title = title
        self.body = body
        self.id = id
        self.kwargs = kwargs

    def __ft__(self):
        print("-------------> RENDERING MODAL BODY")
        return Div(
            Div(
                Div(
                    Div(
                        H3(
                            self.title,
                            cls="text-xl font-semibold text-gray-900 dark:text-white",
                        ),
                        Button(
                            svg.Svg(
                                svg.Path(
                                    stroke="currentColor",
                                    stroke_linecap="round",
                                    stroke_linejoin="round",
                                    stroke_width="2",
                                    d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6",
                                ),
                                aria_hidden="true",
                                xmlns="http://www.w3.org/2000/svg",
                                fill="none",
                                viewbox="0 0 14 14",
                                cls="w-3 h-3",
                            ),
                            Span("Close modal", cls="sr-only"),
                            type="button",
                            data_modal_hide=self.id,
                            cls="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white",
                        ),
                        cls="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600",
                    ),
                    Div(
                        *self.body,
                        id=f"{self.id}-body",
                        cls="p-4 md:p-5 space-y-4",
                    ),
                    Div(
                        Button(
                            "I accept",
                            data_modal_hide=self.id,
                            type="button",
                            cls="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
                        ),
                        Button(
                            "Decline",
                            data_modal_hide=self.id,
                            type="button",
                            cls="py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
                        ),
                        cls="flex items-center p-4 md:p-5 border-t border-gray-200 rounded-b dark:border-gray-600",
                    ),
                    cls="relative bg-white rounded-lg shadow dark:bg-gray-700",
                ),
                cls="relative p-4 w-full max-w-2xl max-h-full",
            ),
            id=f"{self.id}",
            hx_debug="true",
            data_modal_backdrop="static",
            tabindex="-1",
            aria_hidden="true",
            cls="hidden overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full",
        )


class Modal:
    def __init__(self, id: str, title: str, body: Any, button_text: str, **kwargs):
        self.id = id
        self.title = title
        self.body = body
        self.button_text = button_text
        self.kwargs = kwargs

    def __ft__(self):
        return (
            ModalButton(self.button_text, self.id),
            ModalBody(
                title=self.title,
                body=self.body,
                id=self.id,
            ),
        )
