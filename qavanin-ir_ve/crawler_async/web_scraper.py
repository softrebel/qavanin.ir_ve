import logging
from .parser import HTMLLinkExtractor, HTMLParserEachPage
from .core import get_page, get_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """Manages the web scraping process using Selenium WebDriver."""

    def __init__(self):
        """
        Initialize the WebScraper.

        """
        pass

    def get_page_content(self, url, headers={}):
        """
        Get the content of a webpage.

        Args:
            url (str): The URL of the page to scrape.

        Returns:
            str: The page source if successful, None otherwise.
        """
        content = get_page(url, headers)
        if "error-section__title" in content:
            hash = get_hash(content)
            if not hash:
                print("hash error")
                return None
            headers = {"cookie": f"__arcsjs={hash};"}
            content = get_page(url, headers)
        return content


class Scraper:
    """Orchestrates the scraping process using WebScraper and parser classes."""

    def __init__(
        self,
        web_scraper: WebScraper,
        link_parser: HTMLLinkExtractor,
        page_parser: HTMLParserEachPage,
    ):
        """
        Initialize the Scraper.

        Args:
            web_scraper (WebScraper): The WebScraper instance to use.
            link_parser (HTMLLinkExtractor): The link extractor to use.
            page_parser (HTMLParserEachPage): The page parser to use.
        """
        self.web_scraper = web_scraper
        self.link_parser = link_parser
        self.page_parser = page_parser

    def scrape_main_pages(
        self, url_template: str, start_page: int, last_page: int, item_in_page: int
    ):
        """
        Scrape multiple pages using a URL template.

        Args:
            url_template (str): The URL template to use.
            start_page (int): The first page number to scrape.
            last_page (int): The last page number to scrape.
            item_in_page (int): The number of items per page.

        Returns:
            list: A list of page contents.
        """
        content_list = []
        for page_number in range(start_page, last_page + 1):
            url = url_template.format(page_number, page_number, item_in_page)
            content = self.web_scraper.get_page_content(url)
            if content:
                content_list.append(content)
            else:
                logger.warning(f"Skipping page {page_number} due to error")
        return content_list

    def extract_links(self, content_list):
        """
        Extract links from a list of page contents.

        Args:
            content_list (list): A list of page contents.

        Returns:
            list: A list of extracted links.
        """
        all_links = []
        for content in content_list:
            links = self.link_parser.extract_links(content)
            all_links.extend(links)
        return all_links

    def scrape_pages(self, url_template: str, ids: list):
        """
        Scrape individual pages using a list of IDs.

        :Args:
            url_template (str): The URL template to use.
            ids (list): A list of page IDs to scrape.

        returns: A list of page contents.
        """
        pages_html = []
        for _id in ids:
            url = url_template.format(_id)
            content = self.web_scraper.get_page_content(url)
            if content:
                parsed_content = self.page_parser.extract_text(content)
                if parsed_content:  # Only append if content was actually extracted
                    pages_html.append(parsed_content)
            else:
                logger.warning(f"Skipping page with ID {_id} due to error")
        return pages_html