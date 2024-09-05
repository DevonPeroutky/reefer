import fasthtml.svg as svg
from fasthtml.common import Span


class SuccessIcon:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __ft__(self):
        return Span(
            svg.Svg(
                svg.Path(
                    stroke="currentColor",
                    stroke_linecap="round",
                    stroke_linejoin="round",
                    stroke_width="2",
                    d="M1 5.917 5.724 10.5 15 1.5",
                ),
                aria_hidden="true",
                xmlns="http://www.w3.org/2000/svg",
                fill="none",
                viewbox="0 0 16 12",
                cls="w-3.5 h-3.5 text-green-500 dark:text-green-400",
            ),
            cls="absolute flex items-center justify-center w-8 h-8 bg-green-200 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900",
            **self.kwargs,
        )


class SearchIcon:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __ft__(self):
        return Span(
            svg.Svg(
                svg.Path(
                    stroke="currentColor",
                    stroke_linecap="round",
                    stroke_linejoin="round",
                    stroke_width="2",
                    d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z",
                ),
                aria_hidden="true",
                xmlns="http://www.w3.org/2000/svg",
                fill="none",
                viewbox="0 0 20 20",
                cls="w-4 h-4 text-gray-500 dark:text-gray-400",
            ),
            **self.kwargs,
        )
