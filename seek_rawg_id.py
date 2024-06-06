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
from time import sleep
from common.seek_basis import SearchIDSeekerBot

class RawgSeekerBot(SearchIDSeekerBot):
    stores_data = {
        1: {
            "title": "Steam",
            "property": "P1733",
            "regex": r"^https?:\/\/(?:store\.)?steam(?:community|powered)\.com\/app\/(\d+)",
        },
        2: {
            "title": "Microsoft Store",
            "property": "P5885",
            "regex": r"^https?:\/\/www\.microsoft\.com\/(?:[-a-z]+\/)?(?:store\/)?p\/[^\/]+\/([a-zA-Z0-9]{12})",
            "normalize": lambda x: x.lower(),
        },
        3: {
            "title": "PlayStation Store",
            "property": "P5944",
            "regex": r"^https?:\/\/store\.playstation\.com/[-a-z]+\/product\/(UP\d{4}-[A-Z]{4}\d{5}_00-[\dA-Z_]{16})",
        },
        4: {
            "title": "App Store",
            "property": "P3861",
            "regex": r"^https?:\/\/(?:apps|itunes)\.apple\.com\/(?:[^\/]+\/)?app\/(?:[^\/]+\/)?id([1-9][0-9]*)",
        },
        5: {
            "title": "GOG",
            "property": "P2725",
            "regex": r"^https?:\/\/www\.gog\.com\/(?:\w{2}\/)?((?:movie\/|game\/)[a-z0-9_]+)",
        },
        6: {
            "title": "Nintendo eShop",
            "property": "P8084",
            "regex": r"^https?:\/\/www\.nintendo\.com\/(?:store\/products|games\/detail)\/([-a-z0-9]+-(?:switch|wii-u|3ds))",
        },
        7: {
            "title": "Xbox 360 Store",
            "property": "P11789",
            "regex": r"^https://marketplace\.xbox\.com/(?:en-US/)?Product/(?:[^/]+/)?([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12})",
            "normalize": lambda x: x.lower(),
        },
        8: {
            "title": "Google Play",
            "property": "P3418",
            "regex": r"^https?:\/\/play\.google\.com\/store\/apps\/details\?(?:hl=.+&)?id=([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)",
        },
        9: {
            "title": "itch.io",
            "property": "P7294",
            "regex": r"^(https?:\/\/[a-zA-Z0-9\-\_]+\.itch\.io\/[a-zA-Z0-9\-\_]+)",
        },
        11: {
            "title": "Epic Games Store",
            "property": "P6278",
            "regex": r"^https?:\/\/(?:www\.)?(?:store\.)?epicgames\.com\/(?:store\/)?(?:(?:ar|de|en-US|es-ES|es-MX|fr|it|ja|ko|pl|pt-BR|ru|th|tr|zh-CN|zh-Hant)\/)?p(?:roduct)?\/([a-z\d]+(?:[\-]{0,3}[\_]?[^\sA-Z\W\_]+)*)",
        },
    }

    reverse_matching = { entry["property"]: key for key, entry in stores_data.items() }

    def __init__(self):
        super().__init__(
            database_property="P9968",
            default_matching_property="P1733",
            allowed_matching_properties=[entry["property"] for entry in self.stores_data.values()],
        )

        try:
            with open("keys/rawg.key") as keyfile:
                self.api_key = keyfile.read().strip()
        except FileNotFoundError as error:
            raise RuntimeError("RAWG API key unspecified") from error

    def request(self, url, params={}, retries=5):
        try:
            params["key"] = self.api_key
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error:
            if retries <= 0:
                raise
            print("WARNING: request failed; sleeping and retrying...")
            sleep(10)
            return self.request(url, params, retries-1)

    def search(self, query, max_results=3):
        params = {
            "search": query,
            "page_size": max_results,
            "page": 1,
            "stores": self.reverse_matching[self.matching_property],
        }
        json = self.request("https://api.rawg.io/api/games", params=params)
        return [result["slug"] for result in json["results"]]

    def parse_entry(self, entry_id):
        json = self.request(f"https://api.rawg.io/api/games/{entry_id}/stores")

        result = {}
        if "results" in json:
            for store_json in json["results"]:
                store_id = store_json["store_id"]
                if store_id not in self.stores_data:
                    print(f"WARNING: no data for store {store_id} set")
                    continue

                store_data = self.stores_data[store_id]
                prop = store_data["property"]
                regex = store_data["regex"]
                match = re.search(regex, store_json["url"])
                if match:
                    property_value = match.group(1)
                    if "normalize" in store_data:
                        property_value = store_data["normalize"](property_value)
                    result[prop] = property_value
                else:
                    print(f"WARNING: {self.stores_data[store_id]['title']} ID of `{entry_id}` element doesn't match the regex mask")
        return result

if __name__ == "__main__":
    RawgSeekerBot().run()
