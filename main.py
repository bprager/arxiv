#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Path: main.py

import urllib, urllib.request
import os
import logging
from datetime import date, timedelta
from timeit import default_timer as timer
from bs4 import BeautifulSoup
from rich import print
import re
from typing import Union


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(funcName)s:%(lineno)d: %(message)s",
    # handlers=[logging.FileHandler(f"{SCRIPT_DIR}/arxiv.log")],  # NOSONAR
    datefmt="%Y-%m-%d %H:%M:%S",
)


def extract_total_results(html_content: str) -> Union[str, int]:
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the <h1> tag that contains the total results
    h1_tag = soup.find("h1", class_="title")
    if not h1_tag:
        return "Total results not found"

    # Extract the text and use a regular expression to find the total number of results
    h1_text = h1_tag.get_text(strip=True)
    match = re.search(r"of (\d+) results", h1_text)
    if match:
        return int(match.group(1))  # Return as integer
    else:
        return "Total results not found"


def html_to_paper_dict(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    papers = []  # List to store each paper's information

    # Find all paper entries
    for paper_li in soup.find_all("li", class_="arxiv-result"):
        paper_info = {}

        # Extract the arXiv ID
        arxiv_id_tag = paper_li.find("p", class_="list-title").find("a")
        paper_info["arxiv_id"] = arxiv_id_tag.text.strip() if arxiv_id_tag else "N/A"

        # Extract the title
        title_tag = paper_li.find("p", class_="title")
        paper_info["title"] = title_tag.text.strip() if title_tag else "N/A"

        # Extract authors
        authors_tag = paper_li.find("p", class_="authors")
        authors = authors_tag.find_all("a") if authors_tag else []
        paper_info["authors"] = ", ".join(author.text.strip() for author in authors)

        # Extract the full abstract, excluding elements with 'onClick'
        abstract_tag = paper_li.find("span", class_="abstract-full")
        if abstract_tag:
            # Remove elements with 'onClick'
            for onclick_tag in abstract_tag.find_all(onclick=True):
                onclick_tag.decompose()
            paper_info["abstract"] = abstract_tag.get_text(strip=True)
        else:
            paper_info["abstract"] = "N/A"

        papers.append(paper_info)

    return papers


# Get papers from arxiv
def get_papers(start_date: date, end_date: date):
    url = f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date={start_date:%Y-%m-%d}&date-to_date={end_date:%Y-%m-%d}&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first&start=0"
    data = urllib.request.urlopen(url)
    results = data.read().decode("utf-8")
    # logging.debug(f"get_papers: {results}")  # NOSONAR
    return results


def main():
    program_start: float = timer()

    end_date: date = date.today()
    start_date: date = end_date - timedelta(days=1)
    html_content: str = get_papers(start_date, end_date)
    papers = html_to_paper_dict(html_content)
    logging.info(f"found {len(papers)} papers")
    for paper in papers:
        logging.info(f"{paper['title']}")
    logging.info(f"last paper: {papers[-1]}")
    total = extract_total_results(html_content)
    logging.info(f"{total} results found")

    program_end: float = timer()

    logging.info(f"Program took {(program_end - program_start):.2f} seconds to run")


if __name__ == "__main__":
    print("Hello, World!")
    main()
