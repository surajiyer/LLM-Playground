import json
import logging
from time import sleep

from alive_progress import alive_bar
import trafilatura
from courlan.filters import is_navigation_page


logger = logging.getLogger(__name__)


def extract_text(url: str, output_path: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    result = trafilatura.extract(
        downloaded,
        output_format="json",
        include_comments=False,
    )
    with open(output_path, 'a') as f:
        f.write(f"{result}\n")
    return result


def verify_json(filename: str) -> bool:
    with open('data/txtfiles/data.json') as file:
        json.load(file)
    return True


def main():
    SLEEP_TIMEOUT = 3

    with open('data/links.txt', 'r') as f:
        urls_list = f.readlines()
    navigation_links = []
    try:
        with alive_bar(len(urls_list)) as bar:
            for url in urls_list:
                if is_navigation_page(url):
                    logger.warning(f"Navigation page: {url}")
                    navigation_links.append(url)
                    continue
                extract_text(url, output_path='data/txtfiles/data.json')
                sleep(SLEEP_TIMEOUT)
                bar()

    finally:
        with open('data/navigation_links.txt', 'w') as f:
            f.write('\n'.join(navigation_links))


if __name__ == '__main__':
    # main()
    verify_json('data/txtfiles/data.json')
