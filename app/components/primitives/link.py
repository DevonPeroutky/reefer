from typing import Optional
from fasthtml.common import *


class Link:
    def __init__(
        self,
        text: str,
        id: Optional[str] = None,
        **kwargs,
    ):
        self.text = text
        self.id = id
        self.kwargs = kwargs

    def __ft__(self):
        return A(
            self.text,
            id=self.id,
            cls="font-medium text-sky-500 dark:text-sky-500 hover:underline",
            **self.kwargs,
        )
