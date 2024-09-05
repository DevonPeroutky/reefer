import json
import os
import undetected_chromedriver as uc

from typing import List, Optional
from anthropic import Anthropic
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from data_types import JobOpening

PARSE_HTML_SYSTEM_PROMPT = """Your job is to parse html and return structured data as requested. You parse the full document and return all the results. Provide only the answer, with no additional text or explanation."""
PARSE_OPENINGS_LINK_PROMPT = """
This is the list of links tags (containing the content and href) parsed from the html content of the {} careers page. This list contains either a list of job openings, or a link to the list of openings/roles/positions/jobs. Return the link to the page containing openings/roles/positions/jobs. If the current page contains the list then simply return the current link.
Dp not acknowledge this request, simply return only the link, with no additional text or explanation.
"""
PARSE_OPENINGS_PROMPT = """
This is the html content of the {} careers page containing a list of list of openings/roles/positions/jobs, each with a link. Parse the page and return a list of openings with the title of the opening, the link to the specific job page, and the location (if available). Also return a boolean field called related.
Related should return 'True' if the the specific job is related to the criteria {} and 'False' if unrelated. Return the results as a list of json with the keys "title", "link", "location", and "related".
Provide only the JSON, with no additional text or explanation.
"""


class ScrapingService:

    def __init__(self):
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        assert anthropic_api_key, "ANTHROPIC_API_KEY environment variable is not set."
        self.client = Anthropic(api_key=anthropic_api_key)

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
            {"text": a_tag.get_text(), "link": a_tag.get("href")} for a_tag in a_tags
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

    def parse_openings_from_link(
        self,
        company: str,
        job_type: str,
        openings_link: str,
    ) -> List[JobOpening]:
        print(f"Parsing {job_type} openings for {company} from {openings_link}.")
        openings_page_source = self.get_page_source(openings_link)
        cleaned_html = str(self.strip_html(openings_page_source))

        parse_opening_prompt = PARSE_OPENINGS_PROMPT.format(company, job_type)
        prompt = f"{cleaned_html}\n\n {parse_opening_prompt}"
        text_responses = self.create_message(
            PARSE_HTML_SYSTEM_PROMPT,
            prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=4096,
        )
        print(text_responses)
        json_response = json.loads(text_responses)
        print(json_response)
        job_openings = [
            JobOpening(id=str(idx), **json_object)
            for idx, json_object in enumerate(json_response)
        ]
        return job_openings

    def find_openings_page_link(self, company: str, link: str) -> Optional[str]:
        print(f"Parsing openings page link from {link} for {company}")
        raw_html = self.get_page_source(link)
        print("We fetched the page source!!!!")
        links = self.fetch_all_links_from_webpage(raw_html)
        link_prompt = PARSE_OPENINGS_LINK_PROMPT.format(company)
        prompt = f"{links}\n\n {link_prompt}"
        openings_link = self.create_message(
            PARSE_HTML_SYSTEM_PROMPT,
            prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=4096,
        )
        print("Resolved openings link: ", openings_link)

        return ScrapingService.resolve_url(link, openings_link)
