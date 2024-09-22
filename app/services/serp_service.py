from abc import ABC, abstractmethod
import os
from typing import Optional
from pydantic import BaseModel
import requests
import json
import asyncio

from fasthtml.common import S, List
from app import Company, Contact
from exa_py import Exa

from app.services import SearchResult


class SearchClient(ABC):
    def __init__(self, API_KEY: str) -> None:
        self.api_key = API_KEY

    @abstractmethod
    def search(self, query: str) -> List[SearchResult]:
        pass


class ExaClient(SearchClient):
    def __init__(self) -> None:
        if exa_api_key := os.getenv("EXA_API_KEY"):
            self.api_key = exa_api_key
            self.exa = Exa(self.api_key)
        else:
            assert self.api_key, "EXA_API_KEY environment variable is not set."

    def search(self, query: str) -> List[SearchResult]:
        result = self.exa.search_and_contents(
            query,
            type="neural",
            use_autoprompt=True,
            num_results=10,
            text=True,
        )
        return [
            SearchResult(id=r.id, url=r.url, title=r.title or "", snippet=r.text)
            for r in result.results
        ]


class SerpDogClient(SearchClient):
    def __init__(self) -> None:
        self.api_key = os.getenv("SERPDOG_API_KEY")
        assert self.api_key, "SERPDOG_API_KEY environment variable is not set."

    def search(self, query: str) -> List[SearchResult]:

        base_url = "https://api.scrapingdog.com/google"
        url = f"{base_url}?api_key={self.api_key}&query={query}&page=0&results=5"
        print(url)
        resp = requests.get(url)

        print(resp)
        if resp.status_code != 200:
            raise Exception(
                "Failed to fetch search results. Error: ", resp.status_code, resp.reason
            )

        return [
            SearchResult(
                id=str(idx), url=r["link"], snippet=r["snippet"], title=r["title"]
            )
            for idx, r in enumerate(resp.json()["organic_data"])
        ]


class DummySearchClient(SearchClient):
    def __init__(self, API_KEY: str = "dummy") -> None:
        self.api_key = API_KEY

    def search(self, query: str) -> List[SearchResult]:
        return [
            SearchResult(
                id="1",
                url="https://www.brex.com/careers",
                title="Brex",
                snippet="Brex careers page",
            ),
            SearchResult(
                id="2",
                url="https://www.mercury.com",
                title="Mercury",
                snippet="Mercury is another bank",
            ),
        ]


class SearchService(ABC):
    @abstractmethod
    async def find_careers_url(self, company: str) -> str:
        pass

    @abstractmethod
    async def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:
        pass


class SerpService(SearchService):
    def __init__(self, search_client: Optional[SearchClient] = None) -> None:
        if search_client:
            self.api_client = search_client
        else:
            if exa_api_key := os.getenv("EXA_API_KEY"):
                self.api_client = ExaClient()
            elif serp_api_key := os.getenv("SERPDOG_API_KEY"):
                self.api_client = SerpDogClient(API_KEY=serp_api_key)
            else:
                self.api_client = DummySearchClient(API_KEY="DUMMY_API_KEY")
                print(
                    "No API Key found for Exa or SerpDog, using a dummy search client"
                )

    async def find_careers_url(self, company: str) -> str:
        query = "{} careers".format(company)
        res = await asyncio.to_thread(self.api_client.search, query)
        print("Search Results: ", res)

        return res[0].url

    async def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:

        query = "site:linkedin.com/in {} {} {}".format(
            company, " ".join(keywords), " ".join(targetted_roles)
        )
        print("Search QUERY: ", query)
        res = await asyncio.to_thread(self.api_client.search, query)
        print("Search Results: ", res)

        return [
            Contact(
                name=r.title,
                linkedin_url=r.url,
                company=company,
            )
            for r in res
        ]
