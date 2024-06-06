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
Add VK Play ID (P9697) based on matching Steam application ID (P1733).

To get started, type:

    python seek_mailru_id.py -h
"""

import requests
import re
from common.seek_basis import SearchIDSeekerBot

class VKPlaySeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P9697",
            default_matching_property="P1733",
        )

    def search(self, query, max_results=None):
        if len(query) < 3:
            return []

        if not max_results:
            max_results = 5
        elif max_results < 3:
            max_results = 3

        params = {
            "alias": "game",
            "query": query,
            "limit": max_results
        }

        response = requests.get('https://api.vkplay.ru/pc/v3/search/', params=params, headers=self.headers)
        if response:
            return [item["extra"]["slug"] for item in response.json()["items"]]
        else:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")

    def parse_entry(self, entry_id):
        result = ""
        response = requests.get(f"https://api.vkplay.ru/pc/v3/game/{entry_id}/", headers=self.headers)
        try:
            if not response:
                raise RuntimeError("can't get info")
            for item in response.json()["game_urls"]:
                match = re.match(r"https?://store\.steampowered\.com/app/(\d+)", item["url"])
                if not match:
                    continue
                if result:
                    raise RuntimeError("several steam links found")
                result = match.group(1)
        except RuntimeError as error:
            print(f"WARNING: {error} for game `{entry_id}`")
            return {}
        return { "P1733": result }

if __name__ == "__main__":
    VKPlaySeekerBot().run()
