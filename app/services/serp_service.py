from abc import ABC, abstractmethod
import os
import time
import random
import requests
import json

from fasthtml.common import List, Search

from app import Company, Contact
from app.stub_data import test_contacts


class SearchService(ABC):
    @abstractmethod
    def find_careers_url(self, company: str) -> str:
        pass

    @abstractmethod
    def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:
        pass


class SerpService(SearchService):
    def __init__(self):
        self.api_key = os.getenv("SERPDOG_API_KEY")
        assert self.api_key, "SERPDOG_API_KEY environment variable is not set."

    def _search(self, query: str):
        payload = {"api_key": self.api_key, "q": query, "gl": "us"}
        resp = requests.get("https://api.serpdog.io/search", params=payload)
        if resp.status_code != 200:
            raise Exception("Failed to fetch search results. Error: ", resp.status_code)
        return resp.text

    def find_careers_url(self, company: str) -> str:
        query = "{} careers".format(company)
        res = self._search(query)
        results = json.loads(res)["organic_results"]
        # print("Search Results: ", results)

        return results[0]["link"]

    def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:

        # time.sleep(1)
        #
        query = "{} {} {}".format(
            company, " ".join(keywords), " ".join(targetted_roles)
        )
        res = self._search(query)
        results = json.loads(res)["organic_results"]
        print("Search Results: ", results)
        return results


class DummySearchService(SearchService):
    def find_careers_url(self, company: str) -> str:

        time_to_sleep = random.randint(1, 8)
        time.sleep(time_to_sleep)

        return f"https://www.{company}.com/careers"

    def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:
        time_to_sleep = random.randint(1, 8)
        time.sleep(time_to_sleep)

        return test_contacts
