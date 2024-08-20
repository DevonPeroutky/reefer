from typing import Optional
from fasthtml.common import *
import fasthtml.svg as svg

from components.primitives.success_icon import SearchIcon


class SearchInput:
    def __init__(
        self,
        hx_post: str,
        hx_target: str,
        hx_swap: str,
        id: Optional[str] = None,
        hx_indicator: Optional[str] = None,
    ):
        self.hx_post = hx_post
        self.hx_target = hx_target
        self.hx_swap = hx_swap
        self.hx_indicator = hx_indicator
        self.id = id

    def __ft__(self):
        return Form(
            Label(
                "Search",
                fr="search",
                cls="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white",
            ),
            Div(
                Div(
                    SearchIcon(),
                    cls="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none",
                ),
                Input(
                    type="search",
                    id="company",
                    name="company",
                    placeholder="Enter a company name...",
                    required="",
                    cls="block w-full p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                ),
                # Input(
                #     type="text",
                #     id="job_type",
                #     name="job_type",
                #     placeholder="Enter a role...",
                #     required="",
                #     cls="block w-full p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                # ),
                Button(
                    "Search",
                    type="submit",
                    cls="text-white absolute end-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
                    hx_params="job_type=software_engineer",
                ),
                cls="w-[750px] relative",
            ),
            cls="container mx-auto flex justify-center py-10",
            hx_post=self.hx_post,
            hx_target=self.hx_target,
            hx_swap=self.hx_swap,
            hx_indicator=self.hx_indicator,
            id=self.id,
            **{"hx-on:htmx:after-request": "console.log('works.........')"},
        )
