from abc import ABC, abstractmethod
import os
import requests
import json

from fasthtml.common import List

from app import Company, Contact


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
        print(resp)
        if resp.status_code != 200:
            raise Exception(
                "Failed to fetch search results. Error: ", resp.status_code, resp.reason
            )
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

        query = "site:linkedin.com/in {} {} {}".format(
            company, " ".join(keywords), " ".join(targetted_roles)
        )
        print("Search QUERY: ", query)
        res = self._search(query)
        results = json.loads(res)["organic_results"]
        print("Search Results: ", results)

        # CONVERT SERACH RESULTS TO CONTACTS

        return results
