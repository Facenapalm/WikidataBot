# Copyright (c) 2022 Facenapalm
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Add Games@Mail.ru ID (P9697) based on matching Steam application ID (P1733).
# 
# Usage:
# 
#     python mailru_seek_id.py input
# 
# input should be either a path to file with list of items (Qnnn), or a keyword "all"

import pywikibot
from pywikibot import pagegenerators as pg
import requests
import sys
import re

STEAM_PROPERTY = "P1733"
MAILRU_PROPERTY = "P9697"
MAILRU_ITEM = "Q4197758"

def get_steam_id(mailru_slug):
    result = ""
    response = requests.get("https://api.games.mail.ru/pc/v2/game/{}/".format(mailru_slug))
    if not response:
        print("WARNING: can't get info of game `{}`".format(mailru_slug))
        return ""
    for item in response.json()["game_urls"]:
        match = re.match(r"https?://store\.steampowered\.com/app/(\d+)", item["url"])
        if not match:
            continue
        if result:
            print("WARNING: several steam links found for game `{}`".format(mailru_slug))
            return ""
        result = match.group(1)
    return result

def get_search_results(query):
    params = [
        ( "query", query ),
    ]
    response = requests.get('https://api.games.mail.ru/pc/search_suggest/', params=params)
    if response:
        return [result["slug"] for result in response.json()["game"]["items"]]
    else:
        print("WARNING: can't get search results for query `{}`".format(query))
        return []

def process_item(repo, item):
    if item.isRedirectPage():
        print("{}: redirect page".format(item.title()))
        return
    if MAILRU_PROPERTY in item.claims:
        print("{}: Games@Mail.ru ID already set".format(item.title()))
        return
    if STEAM_PROPERTY not in item.claims:
        print("{}: Steam ID not found".format(item.title()))
        return
    if len(item.claims[STEAM_PROPERTY]) > 1:
        print("{}: several Steam IDs found".format(item.title()))
        return
    steam_id = item.claims[STEAM_PROPERTY][0].getTarget()

    if "en" in item.labels:
        lang = "en"
    else:
        # any language is better than none
        lang = [x for x in item.labels][0]

    for mailru_slug in get_search_results(item.labels[lang]):
        candidate_steam_id = get_steam_id(mailru_slug)
        if candidate_steam_id == "":
            continue
        if candidate_steam_id != steam_id:
            continue

        claim = pywikibot.Claim(repo, MAILRU_PROPERTY)
        claim.setTarget(mailru_slug)
        item.addClaim(claim, summary="Add Games@Mail.ru ID based on matching Steam application ID")
        print("{}: added Games@Mail.ru ID `{}`".format(item.title(), mailru_slug))
        return

    print("{}: failed to find Games@Mail.ru ID".format(item.title()))

def main():
    repo = pywikibot.Site()

    if len(sys.argv) > 1:
        source = sys.argv[1]
        if source != "all":
            for item_id in open(source):
                item = pywikibot.ItemPage(repo, item_id)
                process_item(repo, item)
            return

    query = """
        SELECT ?item {{
            ?item p:{} [] .
            FILTER NOT EXISTS {{ ?item p:{} [] }}
        }}
    """.format(STEAM_PROPERTY, MAILRU_PROPERTY)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        process_item(repo, item)

if __name__ == "__main__":
    main()
