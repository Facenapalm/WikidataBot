# Copyright (c) 2024 Facenapalm
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
Add PlayGround.ru ID (P10354) based on matching Steam application ID (P1733).

To get started, type:

    python seek_playground_id.py -h
"""

import requests
import re
from collections import defaultdict
from common.seek_basis import SearchIDSeekerBot

class PlayGroundSeekerBot(SearchIDSeekerBot):
    stores_data = {
        "steam": {
            "title": "Steam",
            "property": "P1733",
            "regex": r"^https?:\/\/(?:store\.)?steam(?:community|powered)\.com\/app\/(\d+)",
        },

        "epicgames": {
            "title": "Epic Games Store",
            "property": "P6278",
            "regex": r"^https?:\/\/(?:www\.)?(?:store\.)?epicgames\.com\/(?:store\/)?(?:(?:ar|de|en-US|es-ES|es-MX|fr|it|ja|ko|pl|pt-BR|ru|th|tr|zh-CN|zh-Hant)\/)?p(?:roduct)?\/([a-z\d]+(?:[\-]{0,3}[\_]?[^\sA-Z\W\_]+)*)",
        },

        "playstationstore": {
            "title": "PlayStation Store concept",
            "property": "P12332",
            "regex": r"^https?:\/\/store\.playstation\.com/(?:[a-z\-]+/)?concept/(\d+)",
        },

        "microsoftstore": {
            "title": "Microsoft Store",
            "property": "P5885",
            "regex": r"https://www\.microsoft\.com/store/productid/([A-Za-z0-9]{12})$",
            "normalize": lambda x: x.lower(),
        },

        "ggsel": None,
        "keysforgamers": None,
        "plati": None,
    }

    def __init__(self):
        super().__init__(
            database_property='P10354',
            default_matching_property='P1733',
            allowed_matching_properties=[entry["property"] for entry in self.stores_data.values() if entry],
        )

    def search(self, query, max_results=None):
        params = [
            ( "query", query ),
            ( "include_addons", 0 )
        ]
        try:
            response = requests.get('https://www.playground.ru/api/game.search', params=params, headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if response:
            return [x['slug'] for x in response.json()]
        else:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")

    def parse_entry(self, entry_id):
        try:
            response = requests.get(f'https://www.playground.ru/shop/{entry_id}/', headers=self.headers, timeout=10)
            if not response:
                raise RuntimeError("can't download info")
            html = response.text

            regex = r"""
                <a\starget="_blank"\s*
                    class="product-item\sjs-product-item"\s*
                    href="/shop/redirect/(\d+)">\s*
                <div\sclass="name">[\s\S]*?</div>\s*
                <div\sclass="secondary">([\s\S]*?)</div>
            """

            stores = defaultdict(list)
            for section in re.findall(r'<div class="section-title">\s*Стандартное издание\s*</div>\s*([\s\S]+?)\s*</div>\s*</div>', html):
                section = re.sub(r'<span class="discount">[\s\S]*?</span>', '', section)
                section = section.replace('(Недоступно в РФ)', '')

                for store_id, store_name in re.findall(regex, section, flags=re.VERBOSE):
                    stores[re.sub(r'\s', '', store_name).lower()].append(store_id)

            result = {}

            for store_name, store_ids in stores.items():
                if store_name not in self.stores_data:
                    print(f'WARNING: unknown store `{store_name}` for `{entry_id}`')
                    continue
                store_data = self.stores_data[store_name]
                if store_data is None:
                    continue
                if len(store_ids) > 1:
                    # TODO: filter duplicate IDs before checking this
                    print(f'WARNING: several {store_data["title"]} links for `{entry_id}`')
                    continue
                response = requests.head(f'https://www.playground.ru/shop/redirect/{store_ids[0]}', allow_redirects=True)
                match = re.search(store_data["regex"], response.url)
                if not match:
                    continue
                property_value = match.group(1)
                if "normalize" in store_data:
                    property_value = store_data["normalize"](property_value)
                result[store_data["property"]] = property_value

            return result
        except (RuntimeError, requests.exceptions.Timeout) as error:
            print(f"WARNING: {error} for game `{entry_id}`")
            return {}

if __name__ == '__main__':
    PlayGroundSeekerBot().run()
