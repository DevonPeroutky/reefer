import random
import time

from app import Company, Contact, JobOpening
from typing import List, Optional, Dict
from app.services.serp_service import SearchService
from app.services.scraping_service import ScrapingService
from app.stub.data import test_contacts, test_openings


class DummySearchService(SearchService):
    def find_careers_url(self, company: str) -> str:

        time_to_sleep = random.randint(1, 2)
        time.sleep(time_to_sleep)

        return f"https://www.{company}.com/careers"

    def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:
        time_to_sleep = random.randint(1, 3)
        time.sleep(time_to_sleep)

        return test_contacts


class DummyScrapingService(ScrapingService):

    def find_openings_page_link(self, company: str, link: str) -> Optional[str]:
        time_to_sleep = random.randint(1, 2)
        time.sleep(time_to_sleep)

        return f"https://www.{company}.com/careers"

    def find_query_terms_from_job_description(
        self, job_opening: JobOpening
    ) -> Dict[str, List[str]]:
        time_to_sleep = random.randint(1, 2)
        time.sleep(time_to_sleep)
        return {
            "keywords": ["Python", "Django", "React", "GraphQL"],
            "positions": [
                "Engineering Manager",
                "Software Engineering",
                "Technical Lead",
            ],
        }

    def parse_openings_from_link(self, job_type, company: Company) -> List[JobOpening]:
        time_to_sleep = random.randint(1, 2)
        time.sleep(time_to_sleep)

        return test_openings
