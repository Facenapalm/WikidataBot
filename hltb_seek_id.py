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

# Add HowLongToBeat ID (P2816) based on matching Steam application ID (P1733).
# 
# Usage:
# 
#     python hltb_seek_id.py input
# 
# input should be either a path to file with list of items (Qnnn), or a keyword "all"

import pywikibot
from pywikibot import pagegenerators as pg
from howlongtobeatpy import HowLongToBeat
import urllib.request
import sys
import re

STEAM_PROPERTY = "P1733"
HLTB_PROPERTY = "P2816"

def get_steam_id(hltb_slug):
    attempts = 3
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }
    url = "https://howlongtobeat.com/game/{}".format(hltb_slug)
    for attempt_no in range(attempts):
        try:
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8", errors="ignore")
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error

    # <strong><a class="text_red" href="https://store.steampowered.com/app/620/" rel="noreferrer" target="_blank">Steam</a></strong>
    matches = re.findall(r"href=\"https://store\.steampowered\.com/app/(\d+)[/\"]", html)
    if len(matches) == 1:
        return matches[0]
    else:
        return ""

def get_search_results(query):
    query = re.sub(" [–—] ", " ", query)
    return [str(entry.game_id) for entry in HowLongToBeat(0.5).search(query)][:5]

def process_item(repo, item):
    if item.isRedirectPage():
        print("{}: redirect page".format(item.title()))
        return
    if HLTB_PROPERTY in item.claims:
        print("{}: HowLongToBeat ID already set".format(item.title()))
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

    def check_slug(hltb_slug):
        candidate_steam_id = get_steam_id(hltb_slug)
        if candidate_steam_id == "":
            return False
        if candidate_steam_id != steam_id:
            return False

        claim = pywikibot.Claim(repo, HLTB_PROPERTY)
        claim.setTarget(hltb_slug)
        item.addClaim(claim, summary="Add HowLongToBeat ID based on matching Steam application ID")
        print("{}: added HowLongToBeat ID `{}`".format(item.title(), hltb_slug))
        return True

    for hltb_slug in get_search_results(item.labels[lang]):
        if check_slug(hltb_slug):
            return

    if lang in item.aliases:
        for alias in item.aliases[lang]:
            search_results = get_search_results(alias)
            if len(search_results) > 0:
                if check_slug(search_results[0]):
                    return

    print("{}: failed to find HowLongToBeat ID".format(item.title()))

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
    """.format(STEAM_PROPERTY, HLTB_PROPERTY)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        process_item(repo, item)

if __name__ == "__main__":
    main()
