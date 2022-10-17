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
Add Mod DB game ID (P6774) based on matching Steam application ID (P1733).

To get started, type:

    python seek_moddb_id.py -h
"""

import requests
import re
from seek_basis import BaseSeekerBot

class ModDBSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q2983178",
            database_prop="P6774",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733", "P2725"],
        )

    def search(self, query, max_results=10):
        params = [
            ( "a", "search" ),
            ( "p", "games" ),
            ( "q", query ),
            ( "l", max_results ),
        ]
        response = requests.get("https://www.moddb.com/html/scripts/autocomplete.php", params=params)
        if response:
            return re.findall(r'href="/games/([^"]+)"', response.text)
        else:
            raise RuntimeError("can't get search results for query `{}`: {}".format(query, response.status))

    def parse_entry(self, entry_id):
        result = {}
        response = requests.get("https://www.moddb.com/games/{}".format(entry_id))
        try:
            if not response:
                raise RuntimeError("can't get info".format(entry_id))
            match = re.search(r'<div class="table tablemenu tableprice">.*?</div>\s*</div>', response.text, flags=re.DOTALL)
            if not match:
                raise RuntimeError("can't get price table")
            tableprice = match.group(0)

            match = re.search(r'href="https?://store\.steampowered\.com/app/(\d+)[/"]', tableprice)
            if match:
                result["P1733"] = match.group(1)
            match = re.search(r'href="https?://www\.gog\.com/(?:en/)?(game/[a-z0-9_]+)[?"]', tableprice)
            if match:
                result["P2725"] = match.group(1)
        except RuntimeError as error:
            print("WARNING: {} for game `{}`".format(error, entry_id))
        return result

if __name__ == "__main__":
    ModDBSeekerBot().run()
