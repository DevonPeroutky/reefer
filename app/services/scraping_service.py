from abc import ABC, abstractmethod
import asyncio
import json
import os
from fasthtml.common import dataclass
import undetected_chromedriver as uc

from typing import Dict, List, Optional
from anthropic import Anthropic
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from app import JobOpening, Company

PARSE_HTML_SYSTEM_PROMPT = """Your job is to simply return structured data as requested. You parse the full document and return all the results. Provide only the answer, with no additional text or explanation. Do not answer with I Understand or similiar"""
PARSE_OPENINGS_LINK_PROMPT = """
This is a JSON list of links parsed from the html content of the {} careers page. This list contains either a list of job openings, or a link to the list of openings/roles/positions/jobs. If the list contains a list of opens or jobs or positions, return None. Otherwise, 
return the link to the open positions/roles/openings. Do not acknowledge this request, do not say Understood, simply return only either the link or None, with no additional text or explanation: \n\n {}
"""
PARSE_OPENINGS_PROMPT = """
This is the html content of the {} careers page containing a list of list of openings/roles/positions/jobs, each with a link. Parse the page and return a list of openings with the title of the opening, the link to the specific job page, and the location (if available). Also return a boolean field called related.
Related should return 'True' if the the specific job is related to the criteria {} and 'False' if unrelated. Return the results as a list of json with the keys "title", "link", "location", and "related".
Provide only the JSON, with no additional text or explanation.
"""
PARSE_QUERY_TERMS_PROMPT = """
This is the html content of the {} job page at {}. I'm trying to find the most relevant hiring manager or employee at {} to reach out to for a referral. 

Parse the page and return two lists:

- The list of keywords or terms that are most relevant to the job description. Stick to skills and technologies, ignore locations and other general words (Ex. if the job is for a "Software Engineer", the list could contain "Python", "Django", "React", "GraphQL" )
- The list of potential relevant positions involved for hiring for this role. (Ex. if the job is for a "Software Engineer", the list could contain "Engineering Manager", "Software Engineering", "Technical Lead" )

The two list should be returned as a JSON with the keys "keywords" and "positions". Provide only the JSON, with no additional text or explanation.
"""


class ScrapingService(ABC):
    @abstractmethod
    async def find_openings_page_link(self, company: str, link: str) -> Optional[str]:
        pass

    @abstractmethod
    async def find_query_terms_from_job_description(
        self, job_opening: JobOpening
    ) -> Dict[str, List[str]]:
        pass

    @abstractmethod
    async def parse_openings_from_link(
        self, job_type: str, company: Company
    ) -> List[JobOpening]:
        pass

    @staticmethod
    def strip_html(raw_html) -> str:
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup(["script", "style", "iframe"]):
            tag.decompose()

        # Iterate over all elements in the soup
        for tag in soup.find_all(True):
            # Remove the class attribute from each tag
            tag.attrs.pop("class", None)

        # List of attributes to preserve
        preserve_attrs = ["id", "href", "datetime"]

        # Iterate over all elements in the soup
        for tag in soup.find_all(True):
            # Get the attributes of the current tag
            attrs = tag.attrs.copy()  # Copy to avoid modifying while iterating

            # Remove all attributes except the ones in preserve_attrs
            for attr in attrs:
                if attr not in preserve_attrs:
                    tag.attrs.pop(attr, None)

        # Remove all comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        return str(soup)

    @staticmethod
    def fetch_all_links_from_webpage(raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        a_tags = soup.find_all("a")
        return [
            {"title": a_tag.get_text().replace("\n", " "), "href": a_tag.get("href")}
            for a_tag in a_tags
        ]

    @staticmethod
    def resolve_url(base_url, link):
        # Parse the link
        parsed_link = urlparse(link)

        # Check if the link is relative (it doesn't have a scheme or netloc)
        if not parsed_link.scheme and not parsed_link.netloc:
            # Combine it with the base URL
            combined_url = urljoin(base_url, link)
            return combined_url
        else:
            # The link is absolute
            return link

    @staticmethod
    def get_page_source(url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless Chrome
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for JavaScript to finish loading
        print("Waiting for javascript to finish loading")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Done.")

        # Wait for the page to load completely (this can be adjusted as needed)
        driver.implicitly_wait(2)

        # Extract text content from the body or specific elements
        # content = driver.find_element(By.TAG_NAME, "body").text
        page_source = driver.page_source

        driver.quit()

        return page_source


class CareersPageScrapingService(ScrapingService):

    def __init__(self):
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        assert anthropic_api_key, "ANTHROPIC_API_KEY environment variable is not set."
        self.client = Anthropic(api_key=anthropic_api_key)

    def create_message(
        self, prompt, system_prompt, model, temperature, max_tokens
    ) -> str:
        message = self.client.messages.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        return message.content[0].text

    async def parse_openings_from_link(
        self,
        job_type: str,
        company: Company,
    ) -> List[JobOpening]:
        print(
            f"Parsing {job_type} openings for {company.name} from {company.opening_link}."
        )
        openings_page_source = await asyncio.to_thread(
            self.get_page_source, company.opening_link
        )
        cleaned_html = str(ScrapingService.strip_html(openings_page_source))
        print(
            f"Reduce the HTML context payload from {len(openings_page_source)} --> {len(cleaned_html)}"
        )

        parse_opening_prompt = PARSE_OPENINGS_PROMPT.format(company.name, job_type)
        prompt = f"{cleaned_html}\n\n {parse_opening_prompt}"
        text_responses = await asyncio.to_thread(
            self.create_message,
            PARSE_HTML_SYSTEM_PROMPT,
            prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=4096,
        )
        json_response = json.loads(text_responses)
        print(json_response)
        job_openings = [
            JobOpening(id=str(idx), company=company, **json_object)
            for idx, json_object in enumerate(json_response)
        ]
        return job_openings

    async def find_openings_page_link(self, company: str, link: str) -> Optional[str]:
        print(f"Parsing openings page link from {link} for {company}")
        raw_html = ScrapingService.get_page_source(link)
        links = self.fetch_all_links_from_webpage(raw_html)
        print("LInks: ", links)
        prompt = PARSE_OPENINGS_LINK_PROMPT.format(company, links)
        print(prompt)
        openings_link = await asyncio.to_thread(
            self.create_message,
            PARSE_HTML_SYSTEM_PROMPT,
            prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=4096,
        )
        print("Resolved openings link: ", openings_link)

        return (
            ScrapingService.resolve_url(link, openings_link)
            if openings_link and openings_link.lower() != "none"
            else None
        )

    async def find_query_terms_from_job_description(
        self, job_opening: JobOpening
    ) -> Dict[str, List[str]]:
        raw_html = ScrapingService.get_page_source(job_opening.link)
        cleaned_html = str(ScrapingService.strip_html(raw_html))

        parse_query_terms_prompt = PARSE_QUERY_TERMS_PROMPT.format(
            job_opening.title, job_opening.company, job_opening.company
        )
        prompt = f"{cleaned_html}\n\n {parse_query_terms_prompt}"
        text_responses = await asyncio.to_thread(
            self.create_message,
            PARSE_HTML_SYSTEM_PROMPT,
            prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=4096,
        )
        print(text_responses)
        json_response = json.loads(text_responses)
        print(json_response)
        return json_response
