# Copyright (c) 2023 Facenapalm
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
Add IndieMag game ID (P9870) based on matching external idenitifiers - for
instance, Steam application ID (P1733).

To get started, type:

    python seek_indiemag_id.py -h
"""

import re
import requests
from common.seek_basis import SearchIDSeekerBot

class IndieMagSeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P9870",
            default_matching_property="P1733",
            allowed_matching_properties=["P1733", "P2725"],
            additional_query_lines=["?item wdt:P136 wd:Q2762504 ."], # indie games only
        )

    def search(self, query, max_results=None):
        try:
            response = requests.get(f'https://www.indiemag.fr/search/node/{query}', headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            print(f"WARNING: query `{query}` resulted in {response.status_code}: {response.reason}")
            return []
        html = response.text
        return re.findall(r'<div class="search-result">\s*<div class="vignette apercu">\s*<div class="image">\s*<a href="/jeux/([a-z0-9\-]+)"', html)

    def parse_entry(self, entry_id):
        try:
            response = requests.get(f'https://www.indiemag.fr/jeux/{entry_id}', headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            print(f"WARNING: video game `{entry_id}` returned {response.status_code}: {response.reason}")
            return {}
        html = response.text

        match = re.search(r'<div class="externes">([\s\S]+?)</div>\s*<div class="clear"></div>', html)
        if not match:
            print(f"WARNING: no external links found for `{entry_id}`")
            return {}
        externals = match.group(1)

        result = {}

        match = re.search(r'href="https?://store\.steampowered\.com/app/(\d+)[/"]', externals)
        if match:
            result["P1733"] = match.group(1)
        match = re.search(r'href="https?://www\.gog\.com/(?:en/)?(game/[a-z0-9_]+)[?"]', externals)
        if match:
            result["P2725"] = match.group(1)

        return result

if __name__ == "__main__":
    IndieMagSeekerBot().run()
