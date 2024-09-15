import asyncio
import random
import time

from app import Company, Contact, JobOpening
from typing import List, Optional, Dict
from app.services.serp_service import SearchService
from app.services.scraping_service import ScrapingService
from app.stub.data import test_contacts, test_openings


class DummySearchService(SearchService):
    async def find_careers_url(self, company: str) -> str:
        await asyncio.sleep(1)

        return f"https://www.{company}.com/careers"

    async def find_list_of_contacts(
        self, company: Company, keywords: List[str], targetted_roles: List[str]
    ) -> List[Contact]:
        await asyncio.sleep(1)
        return test_contacts


class DummyScrapingService(ScrapingService):

    async def find_openings_page_link(self, company: str, link: str) -> Optional[str]:

        await asyncio.sleep(1)
        return f"https://www.{company}.com/careers"

    async def find_query_terms_from_job_description(
        self, job_opening: JobOpening
    ) -> Dict[str, List[str]]:
        await asyncio.sleep(1)
        return {
            "keywords": ["Python", "Django", "React", "GraphQL"],
            "positions": [
                "Engineering Manager",
                "Software Engineering",
                "Technical Lead",
            ],
        }

    async def parse_openings_from_link(
        self, job_type, company: Company
    ) -> List[JobOpening]:
        await asyncio.sleep(1)

        return test_openings
