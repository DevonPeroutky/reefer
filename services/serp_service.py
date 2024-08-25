import os
import requests
import json

from fasthtml.common import List

from data_types import Contact


class SerpService:
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
        self, company: str, keywords: List[str], targetted_role: List[str]
    ) -> List[Contact]:
        return [
            Contact(
                name="John Doe",
                job_title="Software Engineer",
                location="San Francisco",
                email="",
            ),
            Contact(
                name="Jane Smith",
                job_title="Engineering Manager",
                location="San Francisco",
                email="",
            ),
        ]
        query = "{} careers".format(company)
        res = self._search(query)
        results = json.loads(res)["organic_results"]
        # print("Search Results: ", results)
