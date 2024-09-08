from typing import Optional
from fasthtml.common import Any, Span, Div


class Tag:
    def __init__(self, text: str, bg_color_cls: Optional[str] = None, **kwargs):
        self.text = text
        self.kwargs = kwargs
        self.bg_class: str = (
            bg_color_cls or "bg-gray-100 dark:bg-gray-600 dark:text-gray-300"
        )

    def __ft__(self):

        return Div(
            Span(
                self.text,
                cls=f"px-2.5 py-0.5 rounded {self.bg_class} whitespace-nowrap",
            ),
            **self.kwargs,
        )


class JobTypeTag(Tag):
    def __init__(self, text: str, **kwargs):
        super().__init__(
            text, bg_color_cls="bg-sky-100 dark:bg-sky-600 dark:text-sky-300", **kwargs
        )


class CompanyTag(Tag):
    def __init__(self, text: str, **kwargs):
        super().__init__(
            text,
            bg_color_cls="bg-purple-100 dark:bg-purple-600 dark:text-purple-300",
            **kwargs,
        )


class OutputInputTag(Tag):
    def __init__(self, child_node, **kwargs):
        self.child_node = child_node
        self.kwargs = kwargs

    def __ft__(self):
        return Div(
            Span(
                self.child_node,
                cls=f"px-2 py-0.5 rounded border border-green-200 dark:border-green-600 dark:text-green-300 dark:bg-green-600",
            ),
            **self.kwargs,
        )


class KeywordTag(Tag):
    def __init__(self, text: str, **kwargs):
        super().__init__(
            text,
            bg_color_cls="bg-orange-100 dark:bg-orange-600 dark:text-orange-300",
            **kwargs,
        )


class PositionTag(Tag):
    def __init__(self, text: str, **kwargs):
        super().__init__(
            text,
            bg_color_cls="bg-blue-100 dark:bg-blue-600 dark:text-blue-300",
            **kwargs,
        )
