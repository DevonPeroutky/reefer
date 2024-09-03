import os
import time
import requests
import json

from fasthtml.common import List

from data_types import Company, Contact


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
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:

        # time.sleep(1)
        #
        # return [
        #     Contact(
        #         name="Pedro Franceschi",
        #         job_title="Software Engineer",
        #         location="San Francisco",
        #         email="pedro@brex.com",
        #         company=company,
        #     ),
        #     Contact(
        #         name="Jane Smith",
        #         job_title="Engineering Manager",
        #         location="San Francisco",
        #         email="",
        #         company=company,
        #     ),
        # ]
        query = "{} {} {}".format(
            company, " ".join(keywords), " ".join(targetted_roles)
        )
        res = self._search(query)
        results = json.loads(res)["organic_results"]
        print("Search Results: ", results)
        return results
