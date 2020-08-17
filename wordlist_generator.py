#!/usr/bin/env python3
import argparse
from subprocess import PIPE, run
from urllib.parse import urlparse, unquote
import re
import os
import random
import threading
import multiprocessing
import requests


PARSER = argparse.ArgumentParser(description="Simple wordlist generator")
PARSER.add_argument("-domain", "-d", type=str, help="Domain of the target", required=True)
PARSER.add_argument("-threads", "-t", nargs='?', default=multiprocessing.cpu_count(),
                    type=int, help="Threads amount", const=multiprocessing.cpu_count())
PARSER.add_argument("-amount", "-a", nargs='?', default=2000,
                    type=int, help="Amount of gau urls to get", const=2000)

ARGS = PARSER.parse_args()
DOMAIN = ARGS.__dict__["domain"]
GAU_AMOUNT = ARGS.__dict__["amount"]
THREADS_AMOUNT = ARGS.__dict__["threads"]

DENY_LIST = set()
WORDS = set()


def out(command):
    "Return output of the os command"
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True, check=True)
    return result.stdout


def fill_deny_list():
    "Exclude wordlists from 'denylists' folder"
    for filename in os.listdir(os.path.dirname(os.path.realpath(__file__))  + "/denylists/"):
        with open(os.path.dirname(os.path.realpath(__file__))  + "/denylists/" + filename, 'r') as f:
            for line in f:
                DENY_LIST.add(line[:-1].lower())


def add_words(links):
    for line in links:
        url = urlparse(line)
        path = unquote(url.path)
        for word in path.split("/"):
            # Only path symbols, exclude from denylist and remove css pixel args (10px)
            if re.match("^[A-Za-z0-9_-]+$", word) and word.lower() not in DENY_LIST and not re.match("^.*[0-9]px", word):
                # Max domain part length is 63, reduces junk
                if len(word) <= 63 and word not in WORDS:
                    WORDS.add(word)


def words_scrapping(url):
    "Scrape all words on page"
    for i in range(int(GAU_AMOUNT / THREADS_AMOUNT)):
        words = set()
        try:
            response = requests.get(url)
            words.update(unquote(response.text).replace(
                "/", " ").split(" "))
            add_words(words)
        except:
            pass


GAU_URLS = out("gau {} | head -n {}".format(DOMAIN, GAU_AMOUNT)).splitlines()

if not GAU_URLS:
    exit(0)

fill_deny_list()

threads = []
for i in range(THREADS_AMOUNT):
    t = threading.Thread(target=words_scrapping,
                         args=(random.choice(GAU_URLS),))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

for word in WORDS:
    print(word.replace("\n", ""))
