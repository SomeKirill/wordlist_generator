#!/usr/bin/env python3
import argparse
import asyncio
import os
from re import match, search
from subprocess import PIPE, run
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup, Comment

PARSER = argparse.ArgumentParser(
    description="""Unique wordlist generator of unique wordlists.
    Extracts words and comments from pages and URLs.
    By default parses words on 2000 URLs, grabs words and directories from URLs."""
)
PARSER.add_argument(
    "-domain", "-d", type=str, help="Domain of the target", required=True
)

PARSER.add_argument(
    "-comments",
    "-c",
    action="store_true",
    help="Extract only comments with no filtering",
)

PARSER.add_argument(
    "-files",
    "-f",
    action="store_true",
    help="""Extract only filenames.
    E.g 'http://example.com/test.php' will print 'test.php'""",
)

PARSER.add_argument(
    "-dir",
    "-directories",
    action="store_true",
    help="""Extract only directories.
    E.g 'https://hackerone.com/test/folder/' will print 'test', 'folder'""",
)

PARSER.add_argument(
    "-amount",
    "-a",
    nargs="?",
    default=2000,
    type=int,
    help="Amount of gau URLs to fetch",
    const=2000,
)


ARGS = PARSER.parse_args()
DOMAIN = ARGS.__dict__["domain"]
GAU_AMOUNT = ARGS.__dict__["amount"]

DENY_LIST = set()
ALL_WORDS = set()
URL_FILES = set()
URL_DIRS = set()
COMMENTS = set()

MAX_LENGTH = 100


PARSE_ONLY_COMMENTS = ARGS.__dict__["comments"]
PARSE_ONLY_DIRS = ARGS.__dict__["dir"]
PARSE_ONLY_FILES = ARGS.__dict__["files"]


def print_cleaned(word: str):
    "Prints words only if they are not in denylist and 'clean'"
    # Thanks to https://github.com/BonJarber/SecUtils/tree/master/clean_wordlist
    regexes = (
        "[\!(,%\&]",  # Noisy characters
        ".{100,}",  # Lines with more than 100 characters
        "[0-9]{4,}",  # Lines with 4 or more consecutive digits
        "[0-9]{3,}$",  # Lines where the last 3 or more characters are digits
        "[a-z0-9]{32}",  # MD5 hash or similar
        "[0-9]+[A-Z0-9]{5,}",  # Number followed by 5 or more numbers and letters
        "\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",  # Ignore UUIDs
        "[0-9]+[a-zA-Z]+[0-9]+[a-zA-Z]+[0-9]+",  # Ignore multiple numbers and letters
    )

    if word.lower() not in DENY_LIST:
        for regex in regexes:
            if match(regex, word):
                return
        print(word)


def get_cleaned_urls(urls):
    """Returns set of URLs which file extension
    does not match extensions from scraping_deny_extensions.txt"""

    cleaned_urls = urls.copy()

    try:
        with open("scraping_deny_extensions.txt") as file:
            for extension in file:
                for url in cleaned_urls.copy():
                    url_extension = os.path.splitext(urlparse(url).path)[1]

                    if extension[:-1] == url_extension[1:]:
                        cleaned_urls.remove(url)
        return cleaned_urls
    except Exception as e:
        print(e)
        exit(-1)


def command_out(command):
    "Returns output of the os command"
    result = run(
        command,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
        check=True,
    )
    return result.stdout


def load_denylist():
    "Fill set of denywords to exclude them from final wordlist"
    for filename in os.listdir(
        os.path.dirname(os.path.realpath(__file__)) + "/denylists/"
    ):
        with open(
            os.path.dirname(os.path.realpath(__file__)) + "/denylists/" + filename, "r"
        ) as f:
            for line in f:
                DENY_LIST.add(line[:-1].lower())


def add_files(urls):
    """Extract files from gau URLs, not from pages.
    Uses 'parsing_allow_extensions.txt' as allow list.
    Does not includes only numeric files."""

    allow_extensions = set()
    with open("parsing_allow_extensions.txt") as file:
        for extension in file:
            allow_extensions.add(extension[:-1])

    for url in urls:
        parsed_url = urlparse(url)
        file = os.path.basename(parsed_url.path)
        if (
            search("[a-zA-Z]", file)
            and "." in file
            and str(file).split(".")[-1] in allow_extensions
        ):
            URL_FILES.add(file)


def add_directories(urls):
    "Extracts directories"
    for url in urls:
        parsed_url = urlparse(url)
        for directory in parsed_url.path.split("/"):
            if search("[a-zA-Z]", directory) and "." not in directory:
                URL_DIRS.add(directory)


def add_html_words(htmls):
    "Parse html and get words"
    for html in htmls:
        words = set(BeautifulSoup(html, "lxml").find_all(text=True))
        for word in words:
            for cleaned_word in set(
                word.replace("\\n", " ").replace(",", " ").replace(".", " ").split(" ")
            ):
                if match("^[A-Za-z0-9_.]+$", cleaned_word):
                    ALL_WORDS.add(cleaned_word)


def add_comments(pages):
    for page in pages:
        try:
            for comments in BeautifulSoup(page, "lxml").findAll(
                text=lambda text: isinstance(text, Comment)
            ):
                COMMENTS.add(comments.extract())
        except TypeError:
            # If we could not get any pages
            pass


async def get_page(url):
    "Download page and extract text"
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as response:
            try:
                text = await response.text()
                return text
            except UnicodeDecodeError:
                pass


async def start_scraping():
    tasks = []
    for url in gau_urls:
        tasks.append(asyncio.ensure_future(get_page(url)))
        htmls = await asyncio.gather(*tasks)
        return htmls


if __name__ == "__main__":
    gau_urls = set(
        command_out("gau {} | head -n {}".format(DOMAIN, GAU_AMOUNT)).splitlines()
    )

    if not gau_urls:
        exit(0)

    load_denylist()
    cleaned_urls = get_cleaned_urls(gau_urls)

    loop = asyncio.get_event_loop()

    pages = set()

    add_files(gau_urls)
    add_directories(gau_urls)

    if not PARSE_ONLY_DIRS and not PARSE_ONLY_FILES:
        pages = loop.run_until_complete(start_scraping())
        add_html_words(pages)

    # Print wordlist
    if PARSE_ONLY_COMMENTS:
        add_comments(pages)
        for comment in COMMENTS:
            print_cleaned(comment)
    elif PARSE_ONLY_DIRS:
        for directory in URL_DIRS:
            print_cleaned(directory)
    elif PARSE_ONLY_FILES:
        for file in URL_FILES:
            print_cleaned(file)
    else:
        for word in ALL_WORDS:
            print_cleaned(word.replace("\n", ""))
