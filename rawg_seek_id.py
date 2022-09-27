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


# Add RAWG game ID (P9968) based on matching external idenitifiers - for
# instance, Steam application ID (P1733).
# Then use RAWG database to connect Wikidata item with other external IDs - for
# instance, Epic Games Store or Microsoft Store.
# 
# Usage:
# 
#     python rawg_seek_id.py store input
# 
# store is specified by RAWG store ID, e. g. "1" for Steam.
# input should be either a path to file with list of items (Qnnn), or a keyword "all"
# 
# Script requires RAWG API key, place it at ./keys/rawg.key file.

import pywikibot
from pywikibot import pagegenerators as pg
import requests
import sys
import re
import random
import os.path

STORES_DATA = {
    1: {
        "title": "Steam",
        "property": "P1733",
        "regex": r"^https?:\/\/(?:store\.)?steam(?:community|powered)\.com\/app\/(\d+)"
    },
    2: {
        "title": "Microsoft Store",
        "property": "P5885",
        "regex": r"^https?:\/\/www\.microsoft\.com\/(?:[-a-z]+\/)?(?:store\/)?p\/[^\/]+\/([a-zA-Z0-9]{12})"
    },
    3: {
        "title": "PlayStation Store",
        "property": "P5944",
        "regex": r"^https?:\/\/store\.playstation\.com/[-a-z]+\/product\/(UP\d{4}-[A-Z]{4}\d{5}_00-[\dA-Z_]{16})"
    },
    4: {
        "title": "App Store",
        "property": "P3861",
        "regex": r"^https?:\/\/(?:apps|itunes)\.apple\.com\/(?:[^\/]+\/)?app\/(?:[^\/]+\/)?id([1-9][0-9]*)"
    },
    5: {
        "title": "GOG",
        "property": "P2725",
        "regex": r"^https?:\/\/www\.gog\.com\/(?:\w{2}\/)?((?:movie\/|game\/)[a-z0-9_]+)"
    },
    6: {
        "title": "Nintendo eShop",
        "property": "P8084",
        "regex": r"^https?:\/\/www\.nintendo\.com\/(?:store\/products|games\/detail)\/([-a-z0-9]+-(?:switch|wii-u|3ds))"
    },
    # 7: {
    #     "title": "Xbox 360 Store",
    #     "property": "",
    #     "regex": r""
    # },
    8: {
        "title": "Google Play",
        "property": "P3418",
        "regex": r"^https?:\/\/play\.google\.com\/store\/apps\/details\?(?:hl=.+&)?id=([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)"
    },
    9: {
        "title": "itch.io",
        "property": "P7294",
        "regex": r"^(https?:\/\/[a-zA-Z0-9\-\_]+\.itch\.io\/[a-zA-Z0-9\-\_]+)"
    },
    11: {
        "title": "Epic Games Store",
        "property": "P6278",
        "regex": r"^https?:\/\/(?:www\.)?(?:store\.)?epicgames\.com\/(?:store\/)?(?:(?:ar|de|en-US|es-ES|es-MX|fr|it|ja|ko|pl|pt-BR|ru|th|tr|zh-CN|zh-Hant)\/)?p(?:roduct)?\/([a-z\d]+(?:[\-]{0,3}[\_]?[^\sA-Z\W\_]+)*)"
    },
}

def get_api_key():
    """Read API key from file."""
    filename = "keys/rawg.key"
    if os.path.isfile(filename):
        return open(filename).read().strip()
    else:
        raise RuntimeError("RAWG API key unspecified")

def get_search_results(api_key, query, results=5):
    """Make a search request and return list of game slugs."""
    params = [
        ( "key", api_key ),
        ( "search", query ),
        ( "page_size", results ),
        ( "page", 1 ),
    ]
    response = requests.get('https://api.rawg.io/api/search', params=params)
    return [result["slug"] for result in response.json()["results"]]

def get_store_links(api_key, game_slug):
    """
    Return dict with stores that sell this game.

    Result format: { rawg_store_id: value_for_property, … }
    For example: { 1: "874260", 5: "game/the_forgotten_city", 11: "the-forgotten-city" }
    Extra information can be obtained from STORES_DATA dict using rawg_store_id as a key.
    """
    url = "https://api.rawg.io/api/games/{}/stores?key={}".format(game_slug, api_key)
    response = requests.get(url)
    json = response.json()

    result = {}
    if "results" in json:
        for store_info in json["results"]:
            store_id = store_info["store_id"]
            if store_id not in STORES_DATA:
                print("WARNING: no data for store {} set".format(store_id))
                continue
            regex = STORES_DATA[store_id]["regex"]
            match = re.search(regex, store_info["url"])
            if match:
                result[store_id] = match.group(1)
            else:
                print("WARNING: {} ID of `{}` element doesn't match the regex mask".format(STORES_DATA[store_id]["title"], game_slug))
    return result

def seek_rawg_id(api_key, item, store_id):
    """
    Try to find a RAWG element to connect with given Wikidata item.
    If found, return (game_slug, store_links) tuple. See get_store_links()
    documentation for more info about store_links format.
    If not found, throw RuntimeException.
    """
    title = STORES_DATA[store_id]["title"]
    prop = STORES_DATA[store_id]["property"]
    if prop not in item.claims:
        raise RuntimeError("{} ID not found".format(title))
    if len(item.claims[prop]) > 1:
        raise RuntimeError("several {} IDs found".format(title))
    store_value = item.claims[prop][0].getTarget()

    def check_one_slug(slug):
        """Auxiliary function."""
        store_links = get_store_links(api_key, slug)
        if store_id in store_links:
            if store_value == store_links[store_id]:
                return (slug, store_links)
        raise Exception()

    if "en" in item.labels:
        # Since several games matching the name is a possibility, let's check top 3 results.
        for slug in get_search_results(api_key, item.labels["en"], 3):
            try:
                return check_one_slug(slug)
            except Exception:
                continue
        # If the game has several titles, RAWG can use one of the aliases.
        if "en" in item.aliases:
            for alias in item.aliases["en"]:
                try:
                    return check_one_slug(get_search_results(api_key, alias, 1)[0])
                except Exception:
                    continue
    else:
        # any language is better than none
        lang = [x for x in item.labels][0]
        try:
            return check_one_slug(get_search_results(api_key, item.labels[lang], 1)[0])
        except Exception:
            pass

    raise RuntimeError("no suitable RAWG element found")

def add_stores(repo, item, store_links, ignored_stores={}):
    """Add store links as external IDs at given Wikidata item."""
    for store_id, store_value in store_links.items():
        if store_id in ignored_stores:
            continue
        title = STORES_DATA[store_id]["title"]
        prop = STORES_DATA[store_id]["property"]
        if prop in item.claims:
            print("{}: {} ID already set".format(item.title(), title))
            continue

        claim = pywikibot.Claim(repo, prop)
        claim.setTarget(store_value)
        item.addClaim(claim, summary="Add {} ID based on RAWG database.".format(title))
        print("{}: {} ID set to `{}`".format(item.title(), title, store_value))

def process_item(api_key, repo, item, store_id):
    """
    Fully process one item: seek RAWG slug that links to the same store page
    (store is specified as 4th parameter), set RAWG ID at given Wikidata item,
    then optionally set other store links.
    """
    if item.isRedirectPage():
        print("{}: redirect page".format(item.title()))
        return
    if "P9968" in item.claims:
        print("{}: RAWG ID already set".format(item.title()))
        return

    try:
        rawg_id, store_links = seek_rawg_id(api_key, item, store_id)

        title = STORES_DATA[store_id]["title"]
        claim = pywikibot.Claim(repo, "P9968")
        claim.setTarget(rawg_id)
        item.addClaim(claim, summary="Add RAWG ID based on matching {} ID.".format(title))
        print("{}: RAWG ID set to `{}`".format(item.title(), rawg_id))

        add_stores(repo, item, store_links, ignored_stores={store_id})
    except Exception as error:
        print("{}: {}".format(item.title(), error))

def process_item_list(items, store_id):
    """Process all items from the list based on specified store."""
    key = get_api_key()
    repo = pywikibot.Site()
    for q_item in items:
        item = pywikibot.ItemPage(repo, q_item)
        process_item(key, repo, item, store_id)

def process_store(store_id, limit=None):
    """Process items that have a link to a specified store, but no link to RAWG."""
    key = get_api_key()
    repo = pywikibot.Site()
    prop = STORES_DATA[store_id]["property"]
    query = """
        SELECT ?item {{
            ?item p:{} [] .
            FILTER NOT EXISTS {{ ?item p:P9968 [] }}
        }}
    """.format(prop)
    if limit:
        query += "LIMIT {}".format(limit)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        process_item(key, repo, item, store_id)

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print()
        print("    python rawg_seek_id.py store input")
        print()
        print("store is specified by RAWG store ID, e. g. \"1\" for Steam.")
        print("input should be either a path to file with list of items (Qnnn), or a keyword \"all\"")
        return

    try:
        store_id = int(sys.argv[1])
        STORES_DATA[store_id]
    except Exception as error: 
        print("Incorrect store id. Available stores:")
        for store_id, data in STORES_DATA.items():
            print("    {}: {}".format(store_id, data["title"]))
        return

    if sys.argv[2] == "all":
        process_store(store_id)
    else:
        process_item_list(open(sys.argv[2]), store_id)

if __name__ == "__main__":
    main()
