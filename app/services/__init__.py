from typing import Optional
from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    url: str
    title: str
    snippet: Optional[str]
