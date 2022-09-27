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

# Add Riot Pixels ID (P10393) based on matching external identifier (for
# instance, Steam application ID, P1733).
# 
# Usage:
# 
#     python riotpixels_seek_id.py input [base_property]
# 
# Input should a path to file with list of items (Qnnn, one per line), or a
# keyword "all". Base property is an external ID to seek a match for. If
# ommitted, it defaults to "P1733" (Steam application ID).

import pywikibot
from pywikibot import pagegenerators as pg
import urllib.request
import sys
import re
from urllib.parse import quote

RIOTPIXELS_ITEM = "Q19612893"
RIOTPIXELS_PROPERTY = "P10393"

IDS_DATA = [
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://store\.steampowered\.com/app/(\d+)(?:/[^\"]*)?\" target=_blank>Страница в Steam</a>",
        "property": "P1733",
    },
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://www\.gog\.com/(game/[^\"]+)\" target=_blank>Страница в GOG</a>",
        "property": "P2725",
    },
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://www\.epicgames\.com/store/product/([^\"]+)/\" target=_blank>Страница в магазине Epic Games</a>",
        "property": "P6278",
    },
]

VERBOSE_NAMES = {
    "P1733": "Steam application ID",
    "P2725": "GOG application ID",
    "P6278": "Epic Games Store ID",
}

def get_html(url, attempts=3):
    attempts = 10
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }
    for attempt_no in range(attempts):
        try:
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request, timeout=20)
            html = response.read().decode("utf-8")
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error
    return html

def get_external_ids(rp_slug):
    html = get_html("https://ru.riotpixels.com/games/{}/".format(rp_slug))
    result = {}
    for id_data in IDS_DATA:
        match = re.search(id_data["regex"], html)
        if match:
            result[id_data["property"]] = match.group(1)
    return result

def get_search_results(query):
    html = get_html("https://ru.riotpixels.com/search/{}".format(quote(query)))
    return re.findall(r"\"id\": \"games-([a-z0-9\-]+)\"", html)[:20]

def process_item(repo, item, base_property="P1733"):
    if item.isRedirectPage():
        print("{}: redirect page".format(item.title()))
        return
    if RIOTPIXELS_PROPERTY in item.claims:
        print("{}: Riot Pixels ID already set".format(item.title()))
        return
    if base_property not in item.claims:
        print("{}: base property not found".format(item.title()))
        return
    if len(item.claims[base_property]) > 1:
        print("{}: several base properties found".format(item.title()))
        return
    base_value = item.claims[base_property][0].getTarget()

    if "en" in item.labels:
        lang = "en"
    else:
        # any language is better than none
        lang = [x for x in item.labels][0]

    for rp_slug in get_search_results(item.labels[lang]):
        external_ids = get_external_ids(rp_slug)
        if base_property not in external_ids:
            continue
        if external_ids[base_property] != base_value:
            continue

        claim = pywikibot.Claim(repo, RIOTPIXELS_PROPERTY)
        claim.setTarget(rp_slug)
        item.addClaim(claim, summary="Add Riot Pixels ID based on matching {}".format(VERBOSE_NAMES[base_property]))
        print("{}: added Riot Pixels ID `{}`".format(item.title(), rp_slug))

        return

    print("{}: failed to find Riot Pixels ID".format(item.title()))

def main():
    repo = pywikibot.Site()

    if len(sys.argv) > 3:
        print("Usage:")
        print("    python riotpixels_seek_id.py input [base_property]")
        print()
        print("Examples:")
        print("    python riotpixels_seek_id.py input.txt")
        print("    python riotpixels_seek_id.py all P6278")
        return

    if len(sys.argv) == 3:
        base_property = sys.argv[2]
        if base_property not in VERBOSE_NAMES:
            print("Unsupported base property {}, halting".format(base_property))
            return
    else:
        base_property = "P1733"

    if len(sys.argv) >= 2:
        source = sys.argv[1]
        if source != "all":
            for item_id in open(source):
                item = pywikibot.ItemPage(repo, item_id)
                process_item(repo, item, base_property)
            return

    query = """
        SELECT ?item {{
            ?item p:{} [] .
            FILTER NOT EXISTS {{ ?item p:{} [] }}
        }}
    """.format(base_property, RIOTPIXELS_PROPERTY)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        process_item(repo, item, base_property)

if __name__ == "__main__":
    main()
