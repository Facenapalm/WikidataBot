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

"""
Add RAWG game ID (P9968) based on matching external idenitifiers - for
instance, Steam application ID (P1733).
Then use RAWG database to connect Wikidata item with other external IDs - for
instance, Epic Games Store or Microsoft Store.

To get started, type:

    python seek_rawg_id.py -h

Script requires RAWG API key, place it at ./keys/rawg.key file.
"""

import requests
import re
from os.path import isfile
from seek_basis import BaseSeekerBot

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

REVERSE_MATCHING = { entry["property"]: key for key, entry in STORES_DATA.items() }

class RawgSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q108357933",
            database_prop="P9968",
            default_matching_prop="P1733",
            matching_prop_whitelist=[entry["property"] for entry in STORES_DATA.values()],
        )

        filename = "keys/rawg.key"
        if isfile(filename):
            self.api_key = open(filename).read().strip()
        else:
            raise RuntimeError("RAWG API key unspecified")

    def search(self, query, max_results=3):
        params = [
            ( "key", self.api_key ),
            ( "search", query ),
            ( "page_size", max_results ),
            ( "page", 1 ),
            ( "stores", REVERSE_MATCHING[self.matching_prop] ),
        ]
        response = requests.get('https://api.rawg.io/api/games', params=params)
        return [result["slug"] for result in response.json()["results"]]

    def parse_entry(self, entry_id):
        url = "https://api.rawg.io/api/games/{}/stores?key={}".format(entry_id, self.api_key)
        response = requests.get(url)
        json = response.json()

        result = {}
        if "results" in json:
            for store_info in json["results"]:
                store_id = store_info["store_id"]
                if store_id not in STORES_DATA:
                    print("WARNING: no data for store {} set".format(store_id))
                    continue
                prop = STORES_DATA[store_id]["property"]
                regex = STORES_DATA[store_id]["regex"]
                match = re.search(regex, store_info["url"])
                if match:
                    result[prop] = match.group(1)
                else:
                    print("WARNING: {} ID of `{}` element doesn't match the regex mask".format(STORES_DATA[store_id]["title"], entry_id))
        return result

if __name__ == "__main__":
    RawgSeekerBot().run()
