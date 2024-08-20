import fasthtml.svg as svg
from fasthtml.common import Div, Span, Li, H3, P, Ol
from fasthtml.common import ft_html


class TimelineEvent:
    def __init__(self, id, title, status, task_type, hx_swap_oob=False):
        self.id = id
        self.title = title
        self.status = status
        self.task_type = task_type
        self.hx_swap_oob = hx_swap_oob

    def __ft__(self):
        return Li(
            Span(
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
            ),
            H3(self.title, cls="font-medium leading-tight"),
            P("Step details here", cls="text-sm"),
            cls="ms-6",
            id=f"item-{self.id}",
            sse_swap=f"sse-item-{self.id}",
            hx_swap_oob=self.hx_swap_oob,
        )


class Timeline:
    def __init__(self, id: str, events):
        self.id = id
        self.events = events

    def __ft__(self):
        return Ol(
            *self.events,
            id=self.id,
            cls="relative text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-col gap-y-10",
        )
