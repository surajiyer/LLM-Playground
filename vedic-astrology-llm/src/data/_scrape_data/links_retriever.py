from collections import deque
import logging
import os
import time
from typing import Optional

from trafilatura.spider import focused_crawler


logger = logging.getLogger(__name__)


class LinksRetrieval:

    def resume_crawl(
        self,
        url: str,
        to_visit_txt: Optional[str] = None,
        known_urls_txt: Optional[str] = None,
    ):
        to_visit, known_urls = None, None
        if not to_visit_txt:
            to_visit_txt = os.path.join("data", "to_visit.txt")
        else:
            to_visit = deque(self.read_links(to_visit_txt))
        if not known_urls_txt:
            known_urls_txt = os.path.join("data", "links.txt")
        else:
            known_urls = set(self.read_links(known_urls_txt))
        os.makedirs(os.path.dirname(to_visit_txt), exist_ok=True)
        os.makedirs(os.path.dirname(known_urls_txt), exist_ok=True)
        stop = False
        while not stop:
            try:
                max_seen_urls = 10
                if to_visit is None and known_urls is not None:
                    max_seen_urls = len(known_urls) + 10
                to_visit, known_urls = focused_crawler(
                    url,
                    max_seen_urls=max_seen_urls,
                    todo=to_visit,
                    known_links=known_urls,
                )
                stop = len(to_visit) == 0
            except Exception as e:
                logger.error(f"Error ❌: {e}")
                stop = True
            finally:
                self.save_links(to_visit, to_visit_txt)
                self.save_links(known_urls, known_urls_txt)
            logger.info(f"Number of known urls: {len(known_urls)}")
            logger.info(f"Remaining number of links to visit: {len(to_visit)}")
            if stop:
                break
            logger.info("Going to sleep for 5 seconds")
            time.sleep(5)
        logger.info("Done ✅")

    @staticmethod
    def read_links(links_txt: str) -> list[str]:
        links = []
        if os.path.exists(links_txt):
            with open(links_txt, 'r') as f:
                links = f.readlines()
        return links

    @staticmethod
    def save_links(links: list[str], links_txt: str):
        with open(links_txt, 'w') as f:
            for link in links:
                f.write(link + '\n')


if __name__ == '__main__':
    url = "https://www.astrosaxena.in/blogs"
    lr = LinksRetrieval()
    # lr.resume_crawl(url, to_visit_txt="data/to_visit.txt", known_urls_txt="data/links.txt")
    # lr.resume_crawl(url, known_urls_txt="data/links.txt")
    lr.resume_crawl(url)
