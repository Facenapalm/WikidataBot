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
Add Riot Pixels ID (P10393) based on matching external identifier (for
instance, Steam application ID, P1733).

To get started, type:

    python riotpixels_seek_id.py -h
"""

import re
import requests
from requests.adapters import HTTPAdapter
from common.seek_basis import SearchIDSeekerBot

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

class RiotPixelsSeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P10393",
            default_matching_property="P1733",
            allowed_matching_properties=[entry["property"] for entry in IDS_DATA],
        )

        self.session = requests.Session()
        self.session.mount('https://ru.riotpixels.com', HTTPAdapter(max_retries=10))

    def search(self, query, max_results=20):
        response = self.session.get(f"https://ru.riotpixels.com/search/{query}", headers=self.headers, timeout=20)
        if response:
            return re.findall(r"\"id\": \"games-([a-z0-9\-]+)\"", response.text)[:max_results]
        else:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")

    def parse_entry(self, entry_id):
        response = self.session.get(f"https://ru.riotpixels.com/games/{entry_id}/", headers=self.headers, timeout=20)
        if not response:
            raise RuntimeError(f"can't get info ({response.status_code})")
        html = response.text
        result = {}

        for id_data in IDS_DATA:
            match = re.search(id_data["regex"], html)
            if match:
                result[id_data["property"]] = match.group(1)

        return result

if __name__ == "__main__":
    RiotPixelsSeekerBot().run()
